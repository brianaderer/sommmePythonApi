import singleton as singleton
import json
from unidecode import unidecode
from custom_types.UserType import UserType



class Query:
    props = None
    db = None
    retrieved_keys = []
    filtered_cuvees = []
    all_cuvees = []
    excluded_indices = ['found_wine']
    found_wine = False

    def __init__(self):
        self.s = singleton.Singleton()
        self.instantiate_firebase()
        self.reset()

    def reset(self):
        self.filtered_cuvees = []
        self.all_cuvees = []
        self.suggestions = {
            'colors': [],
            'regions': [],
            'appellations': [],
            'cuvees': [],
            'types': [],
            'classes': [],
            'countries': [],
            'producers': [],
            'vintage': [],
            'grapes': [],
            'found_wine': False,
        }
        self.found_wine = False
        self.retrieved_keys = []

    def instantiate_firebase(self):
        if self.db is None:
            self.db = self.s.Firebase.db
        if self.props is None:
            self.props = self.db.collection('properties')

    def update_sub_caches(self):
        pass
        for key in self.s.Cacher.indexed_collections:
            collection = self.props.document('items').collection(f'{key}')
            coll_ref = collection.get()
            data = [{coll.id: coll.to_dict()} for coll in coll_ref]
            for datum in data:
                db_key = self.get_key(datum)
                path = ''
                data_copy = datum[db_key]
                data_copy['value'] = str(datum[db_key]['value'])
                data = self.s.Cacher.get_data(key=f'{key}:' + db_key, path=path)
                if data is None or not len(data):
                    self.s.Cacher.set_data(key=f'{key}:' + db_key, data=data_copy, path=path)
        self.s.Cacher.create_sub_indices()

    def update_producers_cache(self):
        collection = self.props.document('items').collection('producers')
        producers = collection.get()
        producer_data = [{producer.id: producer.to_dict()} for producer in producers]
        for producer in producer_data:
            key = self.get_key(producer)
            path = ''
            self.s.Cacher.set_data(key='producer:' + key, data=producer[key], path=path)

        collection = self.props.document('items').collection('cuvees')
        cuvees = collection.get()
        cuvee_data = [{cuvee.id: cuvee.to_dict()} for cuvee in cuvees]
        for cuvee in cuvee_data:
            key = self.get_key(cuvee)
            path = ''
            self.s.Cacher.set_data(key='cuvee:' + key, data=cuvee[key], path=path)

        collection = self.props.document('items').collection('vintages')
        vintages = collection.get()
        vintage_data = [{vintage.id: vintage.to_dict()} for vintage in vintages]
        for vintage in vintage_data:
            key = self.get_key(vintage)
            path = ''
            self.s.Cacher.set_data(key='vintage:' + key, data=vintage[key], path=path)
        self.s.Cacher.create_producer_index()

    def update_users_cache(self):
        collection = self.db.collection('users')
        users = collection.get()
        user_data = [{user.id: user.to_dict()} for user in users]
        for user in user_data:
            key = self.get_key(user)
            user_obj = UserType(decoded_data=user[key], key=key)
            data = user_obj.return_data()
            path = ''
            self.s.Cacher.set_data(key='users:' + key, data=data, path=path)
        self.s.Cacher.create_user_index()

    def parse_redis_search_results(self, results):
        # The first element is the total number of results
        total_results = results[0]
        # Initialize an empty dictionary to hold the parsed results
        parsed_results = {}

        # Iterate through the results, starting from the second element
        for i in range(1, len(results), 2):
            key = results[i]  # This is the document identifier
            json_data = results[i + 1][1]  # The JSON data is the second element in the list
            # Parse the JSON data into a dictionary
            parsed_results[key] = json.loads(json_data)
        return total_results, parsed_results

    def get_producers(self, filter_value, with_keys=False):
        result = self.s.Cacher.key_search(value=self.s.Cacher.search_prep(filter_value))
        total_results, parsed_results = self.parse_redis_search_results(result)
        producer_data = parsed_results
        if with_keys:
            # Return the entire dictionary if with_keys is True
            filtered_producers = [
                                     {key: producer} for key, producer in producer_data.items()
                                 ][:10]
        else:
            # Return only the values if with_keys is False
            filtered_producers = [
                                     producer for producer in producer_data.values()
                                 ][:10]
        return filtered_producers

    def get_all_from_coll(self, collection):
        return_docs = []
        docs = self.props.document('items').collection(collection).get()
        for doc in docs:
            return_docs.append({doc.id: doc.to_dict()})
        return return_docs

    def return_coll(self, collection):
        return self.get_all_from_coll('producers')
        # return self.s.Cacher.cache_coll_if_not(collection=collection)

    def get_prop_by_key(self, key, collection):
        doc = self.props.document('items').collection(collection).document(key).get()
        return doc.to_dict()

    def get_key(self, local_dict):
        return list(local_dict.keys())[0]

    def cache_key_handler(self, key, collection):
        if key not in self.retrieved_keys:
            self.retrieved_keys.append(key)
            return self.s.Cacher.cache_key_if_not(key=key, collection=collection)
        else:
            return {}

    def filter_cuvees(self, cuvees, filter_text):
        for cuvee in cuvees:
            self.all_cuvees.append(cuvee)
        if filter_text is not None and len(filter_text):
            filtered_cuvees = [
                cuvee for cuvee in cuvees
                if any(filter_text.lower() in unidecode(value).lower() for value in cuvee.values())
            ]
        else:
            filtered_cuvees = cuvees
        for cuvee in filtered_cuvees:
            self.filtered_cuvees.append(cuvee)

    def check_wine(self, cuvee):
        return_docs = []
        docs = (self.db.collection('beverages')
                .where('cuvees', 'array_contains', cuvee)
                .stream())
        for doc in docs:
            self.found_wine = True
            return_docs.append(doc.to_dict())
        return return_docs

    def filter_keys(self, data):
        keys_to_drop = ['skus', 'vintage', 'full_title', 'owners']
        return {k: v for k, v in data.items() if k not in keys_to_drop}

    def parse_incoming_suggestions(self, producer, cuvee, vintage):
        producer_key = self.get_key(producer)
        producer_val = producer[producer_key]
        producer_dict = {
            0: {'owners': producer_val['owners'], 'cuvees': producer_val['cuvees'], 'value': producer_val['value'],
                'db_id': producer_key}}
        cuvee_str = cuvee[self.get_key(cuvee)]
        return [producer_dict, cuvee_str, vintage]

    def parse_redis_search_value(self, data):
        parsed_data = []
        for i in range(1, len(data), 2):
            key = data[i]
            datum = json.loads(data[i + 1][1])
            value = datum
            parsed_data.append({key: value})
        return parsed_data

    def add_to_suggestions(self, coll, data, key=0):
        if {key: data} not in self.suggestions[coll] and len(list(data.keys())):
            self.suggestions[coll].append({key: data})

    def create_cuvee_object(self, cuvee):
        key = self.get_key(cuvee)
        value = cuvee[key]
        return {
            key: {'value': value['value'], 'db_id': key, 'appellations': [], 'colors': [], 'owners': value['owners']}}

    def expand_wine(self, wine):
        return_wine = {}
        for key in list(wine.keys()):
            val = wine[key]
            return_wine[key] = []
            for value in val:
                item_key = self.get_key(value)
                data = self.cache_key_handler(key=item_key, collection=key)
                return_wine[key].append({item_key: data})
        return return_wine

    def get_vintage_object(self, collection, vintage):
        for item in collection:
            for key, value in item.items():
                if value.get('value') == str(vintage):
                    return item
        return False

    def get_vintage(self, vintage):
        vintage_val = str(vintage[self.get_key(vintage)]['value'])
        found_vintage = self.s.Cacher.key_search(key='vintage', value=(vintage_val))
        parsed_vintage = self.parse_redis_search_value(data=found_vintage)
        if not len(parsed_vintage):
            possible_vintages = self.get_all_from_coll('vintage')
            parsed_vintage_val = vintage[self.get_key(vintage)]['value']
            returned_vintage = self.get_vintage_object(collection=possible_vintages, vintage=parsed_vintage_val)
            if not returned_vintage:
                returned_vintage = self.s.Save.create_prop(prop='vintage', data=str(parsed_vintage_val), uid=1)

            key = self.get_key(returned_vintage)
            self.s.Cacher.set_data(key='vintage:' + key, path='', data=returned_vintage[key])
            parsed_vintage = [returned_vintage]
        return parsed_vintage
