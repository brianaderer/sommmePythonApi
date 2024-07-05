from google.cloud.firestore_v1 import FieldFilter

import singleton as singleton
from unidecode import unidecode
import json

class Query:
    props = None
    db = None
    retrieved_keys = []
    filtered_cuvees = []
    all_cuvees = []
    suggestions = {
        'colors': [],
        'regions': [],
        'appellations': [],
        'cuvees': [],
        'types': [],
        'classes': [],
        'countries': [],
        'producers': [],
    }

    def __init__(self):
        self.s = singleton.Singleton()
        self.instantiate_firebase()

    def reset(self):
        self.filtered_cuvees=[]
        self.all_cuvees=[]
        self.suggestions = {
            'colors': [],
            'regions': [],
            'appellations': [],
            'cuvees': [],
            'types': [],
            'classes': [],
            'countries': [],
            'producers': [],
        }
        self.retrieved_keys = []

    def instantiate_firebase(self):
        if self.db is None:
            self.db = self.s.Firebase.db
        if self.props is None:
            self.props = self.db.collection('properties')

    def add_to_suggestions(self, coll, data, key=0):
        if 'value' in data:
            self.suggestions[coll].append({key: data['value']})

    def update_sub_caches(self):
        for key in self.s.Cacher.indexed_collections:
            collection = self.props.document('items').collection(f'{key}')
            coll_ref = collection.get()
            data = [{coll.id: coll.to_dict()} for coll in coll_ref]
            for datum in data:
                db_key = self.get_key(datum)
                path = ''
                data = self.s.Cacher.get_data(key=f'{key}:' + db_key, path=path)
                if data is None or not len(data):
                    self.s.Cacher.set_data(key=f'{key}:' + db_key, data=datum[db_key], path=path)
        self.s.Cacher.create_sub_indices()

    def update_producers_cache(self):
        collection = self.props.document('items').collection('producers')
        producers = collection.get()
        producer_data = [{producer.id: producer.to_dict()} for producer in producers]
        for producer in producer_data:
            key = self.get_key(producer)
            path = ''
            data = self.s.Cacher.get_data(key='producers:' + key, path=path)
            if data is None or not len(data):
                self.s.Cacher.set_data(key='producers:' + key, data=producer[key], path=path)
        self.s.Cacher.create_producer_index()


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

    def get_producers(self, filter_value, with_keys = False):
        #self.update_producers_cache()
        #self.update_sub_caches()
        result = self.s.Cacher.key_search(value = filter_value)
        total_results, parsed_results = self.parse_redis_search_results(result)
        producer_data = parsed_results
        if with_keys:
            # Return the entire dictionary if with_keys is True
            filtered_producers = [
                                     {key: producer} for key, producer in producer_data.items()
                                     if filter_value.lower() in unidecode(producer['value']).lower()
                                 ][:10]
        else:
            # Return only the values if with_keys is False
            filtered_producers = [
                                     producer for producer in producer_data.values()
                                     if filter_value.lower() in unidecode(producer['value']).lower()
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
            return_docs.append(doc.to_dict())
        return return_docs

    def filter_keys(self, data):
        keys_to_drop = ['skus', 'vintage', 'full_title', 'owners']
        return {k: v for k, v in data.items() if k not in keys_to_drop}

    def parse_incoming_suggestions(self, producer, cuvee, vintage):
        producer_dict = {producer['value']: producer['label']}
        cuvee_str = cuvee[self.get_key(cuvee)]
        return [producer_dict, cuvee_str, vintage]

    def parse_redis_search_value(self, data):
        parsed_data = []
        for i in range(1, len(data), 2):
            key = data[i]
            datum = json.loads(data[i+1][1])
            value = datum['value']
            parsed_data.append({key: value})

        return parsed_data

    def assemble_wine_data(self, producer, filter_cuvee, vintage):
        self.reset()
        producer_dict, parsed_cuvee, parsed_vintage = self.parse_incoming_suggestions(producer=producer, cuvee=filter_cuvee, vintage=vintage )
        parsed_producer = producer_dict[self.get_key(producer_dict)]
        if parsed_producer is None:
            possible_producers = self.return_coll('producers')
        else:
            possible_producers = self.get_producers(filter_value=unidecode(parsed_producer), with_keys=True)
        for producer in possible_producers:
            key = self.get_key(producer)
            data = producer[key]
            self.add_to_suggestions(coll='producers', data=data, key=key)
            filter_text = '' if parsed_cuvee is None else parsed_cuvee
            producer_val = producer[key]
            self.filter_cuvees(cuvees=producer_val['cuvees'], filter_text=unidecode(filter_text))
        action_cuvees = self.filtered_cuvees if len(self.filtered_cuvees) else self.all_cuvees
        if len(action_cuvees) == 1:
            cuvee = action_cuvees[0]
            found_wine = self.check_wine(cuvee=cuvee)
            wine = self.filter_keys(found_wine[0])
            self.suggestions=wine
        else:
            for cuvee in action_cuvees:
                key = self.get_key(cuvee)
                returned_cuvee = self.cache_key_handler(key=key, collection='cuvees')
                self.add_to_suggestions(coll='cuvees', data=returned_cuvee, key=key)
                if 'appellations' in returned_cuvee.keys():
                    for appellation in returned_cuvee['appellations']:
                        key = self.get_key(appellation)
                        returned_appellation = self.cache_key_handler(key=key, collection='appellations')
                        self.add_to_suggestions(coll='appellations', data=returned_appellation, key=key)
                        if 'regions' in returned_appellation:
                            regions = (returned_appellation['regions'])
                            for region in regions:
                                key = self.get_key(region)
                                returned_region = self.cache_key_handler(key=key, collection='regions')
                                self.add_to_suggestions(coll='regions', data=returned_region, key=key)
                                if 'countries' in returned_region:
                                    countries = returned_region['countries']
                                    for country in countries:
                                        key = self.get_key(country)
                                        returned_country = self.cache_key_handler(key=key,
                                                                                  collection='countries')
                                        self.add_to_suggestions(coll='countries', data=returned_country, key=key)
                if 'colors' in returned_cuvee.keys():
                    for color in returned_cuvee['colors']:
                        key = self.get_key(color)
                        returned_color = self.cache_key_handler(key=key, collection='colors')
                        self.add_to_suggestions(coll='colors', data=returned_color, key=key)
                        if 'types' in returned_color:
                            types = returned_color['types']
                            for local_type in types:
                                key = self.get_key(local_type)
                                returned_type = self.cache_key_handler(key=key, collection='types')
                                self.add_to_suggestions(coll='types', data=returned_type, key=key)
                                if 'classes' in returned_type:
                                    classes = returned_type['classes']
                                    for class_object in classes:
                                        key = self.get_key(class_object)
                                        returned_class = self.cache_key_handler(key=key, collection='classes')
                                        self.add_to_suggestions(coll='classes', data=returned_class, key=key)
        if filter_cuvee not in self.suggestions['cuvees']:
            self.suggestions['cuvees'].insert(0, filter_cuvee)

        if producer_dict not in self.suggestions['producers']:
            self.suggestions['producers'].insert(0, producer_dict)

        for key in list(self.suggestions.keys()):
            if not len(self.suggestions[key]):
                data = self.s.Cacher.key_search(value='', key=key, limit=False)
                parsed_data = self.parse_redis_search_value(data)
                self.suggestions[key] = parsed_data
        print(self.suggestions)
        return self.suggestions