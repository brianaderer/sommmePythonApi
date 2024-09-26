import singleton
from custom_types.Error import Error
from typing import AnyStr


class Props:

    def __init__(self):
        self.s = singleton.Singleton()
        self.props_ref = self.s.Firebase.db.collection('properties').document('items')

    def get_or_create_term(self, key, values, owner: AnyStr or None = None, create=True):
        return_data = []
        for value in values:
            results = self.s.Cacher.key_search(value, key)
            # if key == 'cuvee':
            #     print({key: value})
            #     print(results)
            if results[0] == 0 and create:
                cache_object = {'value': value, 'owners': [owner]}
                cacher_string = ''
                coll_ref = self.props_ref.collection(key)
                key_filter = self.s.Firebase.FieldFilter('value', '==', value)
                result = coll_ref.where(filter=key_filter)
                docs = result.stream()
                for doc in docs:
                    doc_id = doc.id
                    doc_dict = doc.to_dict()
                    doc_dict['search_text'] = self.s.Cacher.search_prep(value)
                    cacher_string = key + ':' + doc_id
                    return_data.append((doc_id, doc_dict))  # Append as a tuple (doc.id, doc.data)
                if not len(return_data) > 0:
                    doc_ref = self.s.Firebase.db.collection('properties').document('items').collection(key).document()
                    doc_dict = {'value': value, 'owners': [owner], 'search_text': self.s.Cacher.search_prep(value)}
                    doc_ref.set(doc_dict)
                    cacher_string = key + ':' + doc_ref.id
                    return_data.append((doc_ref.id, doc_dict))
                self.s.Cacher.set_data(key=cacher_string, data=cache_object)
            else:
                parsed_results = self.s.Query.parse_redis_search_results(results)
                keys = list(parsed_results[1].keys())
                for key in keys:
                    data = parsed_results[1][key]
                    if data['value'] == value:
                        return_data.append((key, data))

            # @TODO handle too many results error
        # Return the list of tuples after processing all values
        return return_data if return_data else None

    def update_term(self, coll, key, data):
        try:
            doc_ref = self.s.Firebase.db.collection('properties').document('items').collection(coll).document(key)
            doc_ref.set(data)
            cache_key = coll + ':' + key
            result = self.s.Cacher.set_data(key=cache_key, data=data)
        except Exception as e:
            print(f"An error occurred: {e}")
