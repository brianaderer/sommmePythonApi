import singleton as singleton
import redis
import time
from unidecode import unidecode
import re


class Cacher:
    PRODUCER_LOCK = 'producer_lock'
    indexed_collections = ['regions', 'colors', 'appellations', 'types', 'classes', 'countries', 'vintage', 'grapes',
                           'cuvees']

    def __init__(self):
        self.s = singleton.Singleton()
        self.r = redis.Redis(host='localhost', port=6379, decode_responses=True)

    def cache_coll_if_not(self, collection):
        res = self.ensure_key_exists(collection, None)
        if not len(res):
            print('retrieving data')
            data = self.s.Query.get_all_from_coll(collection=collection)
            self.set_data(key=collection, data=data)
            return data
        else:
            return res

    def cache_key_if_not(self, key, collection):
        assembled_key = collection + ':' + key
        res = self.ensure_key_exists(assembled_key, '$')
        if res is None or not len(res['$']):
            data = self.s.Query.get_prop_by_key(key=key, collection=collection)
            self.set_data(key=assembled_key, data=data)
            return data
        else:
            return res

    def ensure_key_exists(self, key, json_key=None, timeout=10):
        # Attempt to acquire the lock
        if not self.lock_or_unlock(True, timeout):
            raise TimeoutError("Failed to acquire lock within the specified timeout period.")

        try:
            # Check if the key exists
            data = self.r.json().get(key, '$')
            if data is None:
                data_dict = {}
            else:
                data_dict = data[0]
            if json_key is not None and json_key not in data_dict:
                data_dict[json_key] = {}
                self.r.json().set(key, '$', data_dict)
        finally:
            # Release the lock
            self.lock_or_unlock(False)

    def check_if_key_exists(self, key):
        return self.r.exists(key)

    def lock_or_unlock(self, lock, timeout=10):
        if lock:
            start_time = time.time()
            while time.time() - start_time < timeout:
                # Try to set the lock (set if not exists)
                if self.r.set(self.PRODUCER_LOCK, '1', nx=True):
                    return True
                time.sleep(0.1)  # Sleep for a short period before retrying
            return False  # Failed to acquire the lock within the timeout period
        else:
            # Delete the lock
            return self.r.delete(self.PRODUCER_LOCK)

    def retrieve_cached_object(self, key):
        return self.ensure_key_exists(key=key)

    def search_prep(self, str):
        return unidecode(re.sub(r'[^\w\s]', '', str).lower().replace(' ', '-'))

    def set_data(self, key, data, path=''):
        if not self.lock_or_unlock(True, 10):
            raise TimeoutError("Failed to acquire lock within the specified timeout period.")

        try:
            data['search_text'] = self.search_prep(str=data['value'])
            result = self.r.json().set(name=key, path='$' + path, obj=data)
            # self.r.expire(key,
            #               3 * 60 * 60)  # Set expiration time to 3 hours (3 hours * 60 minutes/hour * 60 seconds/minute)
            return result
        finally:
            # Release the lock
            self.lock_or_unlock(False)

    def get_data(self, key, path=''):
        if not self.lock_or_unlock(True, 10):
            raise TimeoutError("Failed to acquire lock within the specified timeout period.")

        try:
            return self.r.json().get(key, '$' + path)
        finally:
            # Release the lock
            self.lock_or_unlock(False)

    def key_search(self, value, key='producers', limit=True, num_results=10000):
        # Break the value into words using regex to split by spaces and punctuation
        words = re.findall(r'\w+', value)

        # Construct the search query to match all words, excluding single-letter words
        search_terms = ' '.join([f'@search:*{word.lower()}*' for word in words if len(word) > 1])
        search_command = ['FT.SEARCH', f'{key}_idx', search_terms, 'LIMIT', '0', str(num_results)]

        print(f"Search command: {search_command}")  # Print the search command for debugging

        results = self.r.execute_command(*search_command)
        modified_results = []
        for i, item in enumerate(results):
            if isinstance(item, str) and item.startswith(key + ':'):
                modified_results.append(item[len(key + ':'):])
            else:
                modified_results.append(item)
        return modified_results

    def create_sub_indices(self):
        for collection in self.indexed_collections:
            try:
                index_creation_command = (
                    'FT.CREATE', f'{collection}_idx', 'ON', 'JSON', 'PREFIX', '1', f'{collection}:', 'SCHEMA',
                    '$.search_text', 'AS',
                    'search', 'TEXT'
                )
                # Execute the index creation command
                self.r.execute_command(*index_creation_command)
                print(f"Index '{collection}_idx' created successfully.")
            except redis.exceptions.ResponseError as e:
                pass

    def create_producer_index(self):
        try:
            index_creation_command = (
                'FT.CREATE', 'producers_idx', 'ON', 'JSON', 'PREFIX', '1', 'producers:', 'SCHEMA', '$.search_text',
                'AS',
                'search', 'TEXT'
            )
            self.r.execute_command(*index_creation_command)
            print("Index 'producers_idx' created successfully.")
        except redis.exceptions.ResponseError as e:
            print(e)

    def create_user_index(self):
        try:
            index_creation_command = (
                'FT.CREATE', 'users_idx', 'ON', 'JSON', 'PREFIX', '1', 'users:', 'SCHEMA', '$.search_text',
                'AS',
                'search', 'TEXT'
            )
            self.r.execute_command(*index_creation_command)
            print("Index 'users_idx' created successfully.")
        except redis.exceptions.ResponseError as e:
            print(e)

        # try:
        #     index_creation_command = (
        #         'FT.CREATE', 'cuvees_by_producer_idx', 'ON', 'JSON', 'PREFIX', '1', 'producers:', 'SCHEMA', '$.value', 'AS',
        #         'value', 'TEXT'
        #     )
        #     # Execute the index creation command
        #     self.r.execute_command(*index_creation_command)
        #     print("Index 'producers_idx' created successfully.")
        # except redis.exceptions.ResponseError as e:
        #     print(e)


    def get_collection(self, class_name):
        index = class_name.replace('"', '')
        # Perform the FT.SEARCH command to return all documents
        return self.r.execute_command('FT.SEARCH', f"{index}_idx", '*', 'LIMIT', 0, 10000000)
