import singleton
import os
import time
from custom_types.Wine import Wine
from custom_types.Flight import Flight
from custom_types.Error import Error
import re


class Save:
    response = {}
    filename = None
    props = None
    path = None
    owner_id = 0
    correlations = {
        'producers': ['cuvees'],
        'cuvees': ['appellations', 'colors'],
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
