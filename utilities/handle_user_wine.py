import json

import singleton as singleton

class HandleUserWine:
    wine = None
    flight = None
    id = None
    producer_name = None
    found_wine = {}
    wine_identity = [
        'countries',
        'producers',
        'cuvees',
        'vintage',
    ]
    has_identity = False

    def __init__(self):
        self.s = singleton.Singleton()
        self.FieldFilter = self.s.Firebase.FieldFilter

    def check_for_id(self):
        for attr in self.wine_identity:
            if attr not in list(self.found_wine.keys()):
                return False
        return True

    def search_vals(self):
        collection_ref = self.s.Firebase.db.collection('beverages')

        # Query to find documents where 'producers' array contains a map with 'Churton' as a value
        query = collection_ref.where('producers', 'array_contains', {'W5bmrJ6UjHiWe0U7YAwK': 'Domaine Tawse'}
)

        # Execute the query and print the results
        results = query.stream()
        for doc in results:
            pass
            # print(f'{doc.id} => {doc.to_dict()}')
    def convert_to_firestore_val(self, key, val):
        wine_val = self.wine[key]
        label = ''
        for item in wine_val:
            if list(item.keys())[0] == val:
                label = list(item.values())[0]['value']
                break
        return {val: label}

    def handle_upload(self, flight, wine):
        self.found_wine = {}
        self.parse_incoming(flight, wine)
        for key in list(self.wine.keys()):
            for attr in self.wine[key]:
                array = list(attr.keys())
                for key_val in array:
                    if key_val and key_val != 0 and key_val != '0':
                        if key not in self.found_wine:
                            self.found_wine[key] = []
                        self.found_wine[key].append(key_val)
            # print(key)
            # print(list(self.wine[key].values()))
        has_all_attrs = self.check_for_id()
        self.search_vals()
        for key, vals in self.found_wine.items():
            for val in vals:
                print(key)
                print(val)
                print(self.convert_to_firestore_val(key=key, val=val))
        return True

    def parse_incoming(self, flight, wine):
        self.wine = json.loads(wine)
        self.flight = json.loads(flight)
        self.id = self.flight['id']
