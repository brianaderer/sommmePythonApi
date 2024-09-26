import singleton
import os
import time
from custom_types.Wine import Wine
from custom_types.Flight import Flight
from custom_types.Error import Error
import re
from custom_types.LongformItem import LongformItem
from custom_types.ShortformItem import ShortformItem


class Save:
    response = {}
    filename = None
    props = None
    path = None
    owner_id = 0
    ban_keys = ['producer', 'cuvee', 'vintage']
    correlations = {
        'producer': ['cuvee'],
        'cuvee': ['appellations', 'colors'],
        'appellations': ['regions', 'countries'],
        'regions': ['countries'],
        'skus': ['sizes', 'cases'],
        'colors': ['types', 'classes'],
        'types': ['classes'],
        'grapes': ['colors', 'types'],
    }
    skip_terms = ['full_title', 'sizes', 'skus', 'cases']
    rich_wine = {}
    rich_wines = []

    def __init__(self):
        self.s = singleton.Singleton()
        self.instantiate_firebase()

    def reset(self):
        self.rich_wine = {}
        self.rich_wines = []

    def instantiate_firebase(self):
        if self.props is None:
            db = self.s.Firebase.db
            self.props = db.collection('properties')
            self.bevs = db.collection('beverages')
            self.flights = db.collection('flights')

    def is_list(self, item):
        return isinstance(item, list)

    def is_error(self, item):
        return isinstance(item, Error)

    def get_collection(self, wine):
        return (next(iter(wine['classes'][0].values()))).lower()

    def title_case(self, sentence):
        # This function uses regular expressions to find words and capitalize them
        return re.sub(r"[A-Za-z]+('[A-Za-z]+)?",
                      lambda mo: mo.group(0)[0].upper() + mo.group(0)[1:].lower(),
                      sentence)

    def combine_unique_dicts(self, list1, list2):
        """
        Safely combines two lists of dictionaries into a single list, containing no duplicates.

        :param list1: The first list of dictionaries.
        :param list2: The second list of dictionaries.
        :return: A new list containing the unique dictionaries from both lists.
        """
        if not isinstance(list1, list) or not all(isinstance(d, dict) for d in list1):
            raise ValueError("list1 must be a list of dictionaries")

        if not isinstance(list2, list) or not all(isinstance(d, dict) for d in list2):
            raise ValueError("list2 must be a list of dictionaries")

        combined_list = list1.copy()  # Start with a copy of list1

        for dict2 in list2:
            if dict2 not in combined_list:
                combined_list.append(dict2)

        return combined_list

    def create_flight(self, wines, owner_id):
        # indices = list(range(len(wines)))
        # flight = {
        #     'wines': wines,
        #     'owner': self.owner_id,
        #     'timestamp': int(time.time()),
        #     'name': self.title_case(self.filename.replace('.pdf', '')),
        #     'versions': {'1': indices},
        #     'currentVersion': 1,
        # }
        # doc_ref = self.flights.document()
        # doc_ref.set(flight)
        self.response = self.s.Flight.create_flight(wines=wines,
                                                    owner_id=self.owner_id,
                                                    name=self.title_case(self.filename.replace('.pdf', '')),
                                                    flights=self.flights,
                                                    response=self.response
                                                    )

    def get_document_by_id(self, doc_id, coll):
        doc_ref = coll.document(doc_id)
        doc = doc_ref.get()
        if doc.exists:
            return doc_ref  # Return the DocumentReference for updates
        else:
            # print("No document found with ID:", doc_id)
            return None  # Or handle it differently depending on your requirements

    def update_terms(self, wine):
        for field, value in wine.items():
            if field not in self.correlations:
                continue
            collection = self.props.document('items').collection(field)
            correlations = self.correlations[field]
            for term in value:
                (key, local_value) = list(term.items())[0]
                document_ref = self.get_document_by_id(key, collection)  # Ensure this is a DocumentReference
                if document_ref is not None:
                    doc_snapshot = document_ref.get()
                    if doc_snapshot.exists:
                        doc_data = doc_snapshot.to_dict()
                        data_to_update = {}
                        for correlation in correlations:
                            if correlation in wine:
                                new_value = wine[correlation]
                                existing_value = doc_data.get(correlation, [])
                                # Merging lists containing dictionaries
                                if isinstance(existing_value, list) and isinstance(new_value, list):
                                    updated_list = self.merge_lists_of_dicts(existing_value, new_value)
                                    if updated_list != existing_value:
                                        data_to_update[correlation] = updated_list
                                elif existing_value != new_value:
                                    data_to_update[correlation] = new_value
                        if data_to_update:
                            document_ref.update(data_to_update)
                            path = field + ':' + document_ref.id
                            data_array = self.s.Cacher.get_data(key=path)
                            data = data_array[0]
                            data_keys = list(data.keys())
                            update_keys = list(data_to_update.keys())
                            for key in update_keys:
                                if key in data_keys:
                                    data[key] = self.combine_unique_dicts(data[key], data_to_update[key])
                                else:
                                    data[key] = data_to_update[key]
                            self.s.Cacher.set_data(key=field + ':' + document_ref.id, data=data)

    def merge_lists_of_dicts(self, list1, list2):
        """
        Merge two lists of dictionaries, combining dictionaries based on their content,
        avoiding duplicates.
        """
        temp_dict = {}
        for d in list1 + list2:
            # Here we convert dictionary items to a hashable form - tuple of tuples
            key = tuple(sorted(d.items()))
            if key not in temp_dict:
                temp_dict[key] = d
        return list(temp_dict.values())

    def are_values_equal(self, val1, val2):
        """
        Compares two values which can be lists of dictionaries, individual dictionaries, or plain values.
        """
        if isinstance(val1, list) and isinstance(val2, list):
            return self.are_lists_equal(val1, val2)
        elif isinstance(val1, dict) and isinstance(val2, dict):
            return self.are_dicts_equal(val1, val2)
        else:
            return val1 == val2

    def are_lists_equal(self, list1, list2):
        """
        Checks if two lists are equal, including lists of dictionaries.
        """
        if len(list1) != len(list2):
            return False
        return all(self.are_values_equal(item1, item2) for item1, item2 in zip(list1, list2))

    def are_dicts_equal(self, dict1, dict2):
        """
        Deep comparison of two dictionaries.
        """
        if dict1.keys() != dict2.keys():
            return False
        return all(self.are_values_equal(dict1[key], dict2[key]) for key in dict1)

    def check_looped_terms(self, wine: Wine):
        bev_ref = self.bevs
        for key in wine.keys:
            if key in self.skip_terms:
                continue
            value = wine.get(key)
            if len(value) > 0:
                key_filter = self.s.Firebase.FieldFilter(key, '==', value)
                docs = bev_ref.where(filter=key_filter)
                documents = docs.stream()
                return documents
        return None

    def dict_to_tuple(self, dict_object):
        key = list(dict_object.keys())[0]
        value = dict_object[key]
        value['search_text'] = self.s.Cacher.search_prep(str(value['value']))
        value['owners'] = None
        return key, value

    def get_vintage_by_val(self, vintage):
        coll_ref = self.s.Firebase.db.collection('properties').document('items').collection('vintage')

        val = vintage[1]['value']
        res = self.s.Cacher.key_search(str(val), 'vintage')
        data = self.s.Query.parse_redis_search_results(res)
        if data[0] < 1:
            vintage_filter = self.s.Firebase.FieldFilter('value', '==', str(val))
            docs = (coll_ref
                    .where(filter=vintage_filter)
                    .stream()
                    )
            for doc in docs:
                return {doc.id: doc.to_dict()}
        else:
            return data[1]
        write_data = vintage[1].copy()
        write_data['owners'] = 1
        write_data['value'] = str(val)
        doc_ref = coll_ref.document()
        doc_ref.set(write_data)
        self.s.Cacher.set_data(key='vintage:' + str(doc_ref.id), data=write_data)
        return {doc_ref.id: write_data}

    def assemble_wine_data(self, producer, filter_cuvee, vintage):
        self.reset()
        producer_object = LongformItem(self.dict_to_tuple(producer))
        cuvee_object = LongformItem(self.dict_to_tuple(filter_cuvee))
        vintage_inter = self.get_vintage_by_val(self.dict_to_tuple(vintage))
        vintage_object = LongformItem(self.dict_to_tuple(vintage_inter))
        # wine.producers_handler(producer_object.get_value())
        # wine.cuvees_handler(cuvee_object.get_value())
        # wine.create_rich_wine()
        return_dict = {'producer': [], 'cuvee': [], 'vintage': [], 'countries': [], 'classes': [], 'grapes': [], 'regions': [], 'types': [], 'appellations': [], 'colors': []}
        return_dict = self.get_values_from_return_dict(producer=producer_object, cuvee=cuvee_object, vintage=vintage_object,
                                                       return_dict=return_dict)
        return return_dict

    def get_values_from_return_dict(self, cuvee: LongformItem, producer: LongformItem, vintage: LongformItem, return_dict):
        # Initialize filters as None
        cuvee_filter = None
        producer_filter = None
        return_dict['vintage'].append(vintage.get_value_dict())

        if producer.key != 0:
            return_dict['producer'].append(producer.get_value_dict())
            producer_filter = self.s.Firebase.FieldFilter('producer', '==', producer.get_shortform_dict())

        if cuvee.key != 0:
            return_dict['cuvee'].append(cuvee.get_value_dict())
            cuvee_filter = self.s.Firebase.FieldFilter('cuvee', '==', cuvee.get_shortform_dict())

        col_ref = self.s.Firebase.db.collection('beverages')

        # Apply filters conditionally
        query = col_ref
        if cuvee_filter:
            query = query.where(filter=cuvee_filter)
        if producer_filter:
            query = query.where(filter=producer_filter)

        # Execute query and process the documents
        docs = query.stream()
        for doc in docs:
            return_dict = self.parse_wine_terms(doc.to_dict(), return_dict)
        return_dict['foundWine'] = producer.key and producer.key != 0 and cuvee.key and cuvee.key != 0
        return return_dict

    def parse_wine_terms(self, wine_dict, return_dict):
        for key in wine_dict:
            if key in return_dict:
                if key not in self.ban_keys:
                    for value in wine_dict[key]:
                        value_object = ShortformItem(value)
                        if value_object.return_value_dict() not in return_dict[key]:
                            return_dict[key].append(value_object.return_value_dict())

        return return_dict

    def save_all_wines(self, all_wines: Flight):
        for wine in all_wines.wines:
            wine: Wine
            wine.create_rich_wine()
            temp_id = wine.identify()
            wine_id = temp_id if temp_id else wine.create()
            wine.ref_id = wine_id
        all_wines.create_flight()


    def create_prop(self, prop, data, uid):
        doc_ref = self.props.document('items').collection(prop).document()
        set_data = {'value': data, 'owners': [uid]}
        doc_ref.set(set_data)
        self.s.Cacher.set_data(key=prop + ':' + doc_ref.id, data=set_data)
        return {doc_ref.id: set_data}
