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
    creates = {}
    has_identity = False
    built_wine = {}

    def __init__(self):
        self.s = singleton.Singleton()
        self.FieldFilter = self.s.Firebase.FieldFilter

    def check_for_id(self):
        for attr in self.wine_identity:
            if attr not in list(self.found_wine.keys()):
                return False
        return True

    def convert_to_firestore_val(self, key, val):
        wine_val = self.wine[key]
        label = ''
        for item in wine_val:
            if list(item.keys())[0] == val:
                label = list(item.values())[0]['value']
                break
        return {val: label}

    def create_in_db(self):
        print(self.creates)

    def handle_upload(self, flight, wine, owner):
        self.parse_incoming(flight, wine)
        for key in list(self.wine.keys()):
            for attr in self.wine[key]:
                array = list(attr.keys())
                for key_val in array:
                    value = attr[key_val]['value']
                    if key not in self.creates:
                        self.creates[key] = []
                    self.creates[key].append(value)
        for key, vals in self.found_wine.items():
            for val in vals:
                self.built_wine[key] = self.convert_to_firestore_val(key=key, val=val)
        self.s.Save.create_rich_wine(self.creates, owner)
        update_wine = self.s.Save.rich_wines[0]
        self.s.Save.update_terms(update_wine)
        # print(self.built_wine)
        # print(self.s.Save.correlations)
        return True

    def parse_incoming(self, flight, wine):
        self.s.Save.rich_wines = []
        self.s.Save.rich_wine = {}
        self.found_wine = {}
        self.creates = {}
        self.producer_name = None
        self.has_identity = False
        self.wine = None
        self.id = None
        self.flight = None
        self.wine = json.loads(wine)
        self.flight = json.loads(flight)
        self.id = self.flight['id']
