import singleton
import os
import time
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
        'appellations': ['regions'],
        'regions': ['countries'],
        'skus': ['sizes', 'cases'],
        'colors': ['types'],
        'types': ['classes']
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

    def check_looped_terms(self, wine):
        query = self.bevs
        for field, value in wine.items():
            if field in self.skip_terms:
                continue
            query = query.where(field, '==', value)

        # After building the query with all necessary conditions, retrieve the documents
        documents = query.get()
        return documents

    def is_list(self, item):
        return isinstance(item, list)

    def get_collection(self, wine):
        return (next(iter(wine['classes'][0].values()))).lower()

    def title_case(self, sentence):
        # This function uses regular expressions to find words and capitalize them
        return re.sub(r"[A-Za-z]+('[A-Za-z]+)?",
                      lambda mo: mo.group(0)[0].upper() + mo.group(0)[1:].lower(),
                      sentence)

    def create_flight(self, wines, owner_id):
        flight = {
            'wines': wines,
            'owner': self.owner_id,
            'timestamp': int(time.time()),
            'name': self.title_case(self.filename.replace('.pdf', '')),
        }
        doc_ref = self.flights.document()
        doc_ref.set(flight)
        self.response.update({'flight_id': doc_ref.id})
        # print(f"Flight with ID {doc_ref.id} has been created with the following wines: {wines}")

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
                (key, local_value), = term.items()
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
            #                 print(f"Updated document at {key} with data: {data_to_update}")
            #             else:
            #                 print(f"No updates needed for {key}; data is identical.")
            #         else:
            #             print(f"Document {key} not found, unable to update.")
            #     else:
            #         print(f"Document reference for {key} not retrieved, unable to update.")
            # print('\n')

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

    def save_all_wines(self, all_wines):
        wine_flight = []
        for wine in all_wines:
            self.create_rich_wine(self.s.Parser.parse_wine(wine))
        for rich_wine in self.rich_wines:
            documents = self.check_looped_terms(rich_wine)
            if len(documents) == 0:
                new_doc_ref = self.bevs.document()  # Create a new document with an auto-generated ID
                del rich_wine['sizes']
                del rich_wine['cases']
                new_doc_ref.set(rich_wine)  # Upload the entire dictionary as the document
                wine_flight.append(new_doc_ref.id)
            else:
                wine_flight.append(documents[0].id)

        self.create_flight(wine_flight, 0)
        for rich_wine in self.rich_wines:
            self.update_terms(rich_wine)
        try:
            os.remove(self.path)
            self.response.update({'deleted': True})
        except:
            self.response.update({'deleted': False})

    def get_term(self, key, wine):
        if self.is_list(wine[key]):
            items = wine[key]
        else:
            items = [wine[key]]
        # Get the collection reference where the documents would be
        for item in items:
            collection_ref = self.props.document('items').collection(key)
            # Query to find documents where the 'value' field is the same as wine[key]
            documents = collection_ref.where(field_path='value', op_string='==', value=item).get()

            if documents:
                # If documents are found, print and return the ID of the first document found
                doc_id = documents[0].id
                # print(f"Document with the same value already exists, ID: {doc_id}")
                return {doc_id: item}
            else:
                # If no documents are found, create a new one
                new_doc_ref = collection_ref.document()  # Create a new document reference
                new_doc_ref.set({'value': item})
                # print("New document created with ID:", new_doc_ref.id)
                return {new_doc_ref.id: item}

    def create_rich_wine(self, wine):
        key_list = ''
        if not hasattr(self, 'rich_wine'):
            self.rich_wine = {}  # Initialize rich_wine as a dictionary if not already done

        if not hasattr(self, 'rich_wines'):
            self.rich_wines = []  # Initialize rich_wines as a list if not already done

        for key in wine:
            if key not in self.rich_wine:
                self.rich_wine[key] = []  # Ensure there is a list to append to

            term = self.get_term(key, wine)  # Avoid using 'id' as it is a built-in function
            self.rich_wine[key].append(term)

        self.rich_wines.append(self.rich_wine.copy())  # Append a copy of the rich_wine to preserve its current state
        self.rich_wine = {}
