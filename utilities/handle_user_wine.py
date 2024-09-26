import json
from custom_types.Flight import Flight
import singleton as singleton
from custom_types.Wine import Wine


class HandleUserWine:
    wine = None
    flight = None
    flight_id = None
    flight_object = None
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
        self.reset()

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

    def handle_upload(self, flight, wine, owner):
        self.parse_incoming(flight, wine)
        self.flight_object = Flight()
        return self.flight_dict_to_object()

    def reset(self):
        self.s.Save.reset()
        self.wine = None
        self.flight = None
        self.flight_id = None
        self.producer_name = None
        self.found_wine = {}
        self.creates = {}
        self.has_identity = False
        self.built_wine = {}
        self.flight_object = None

    def parse_incoming(self, flight, wine):
        self.reset()
        self.wine = json.loads(wine)
        flight = json.loads(flight)
        print(flight)
        doc = self.s.Firebase.db.collection('flights').document(flight['id']).get()
        self.flight = doc.to_dict()
        self.flight_id = flight['id']

    def flight_dict_to_object(self):
        self.flight_object = Flight()
        print(self.flight)
        current_version, versions, wines, owner_id = self.flight['currentVersion'], self.flight['versions'], \
            self.flight['wines'], self.flight['owner']
        self.flight_object.current_version = current_version
        self.flight_object.versions = versions
        self.flight_object.wine_ids = wines
        wine_object = Wine()
        wine_object.parse_wine_dict(self.wine)
        wine_object.create_rich_wine()
        identity = wine_object.identify()
        if not identity:
            wine_id = wine_object.create()
        else:
            wine_id = identity
        for wine in wines:
            temp_wine_object = Wine()
            temp_wine_object.ref_id = wine
            self.flight_object.append_wine(temp_wine_object, owner_id)
        if wine_id not in wines:
            wine_object.ref_id = wine_id
            self.flight_object.append_wine(wine_object, owner_id)
            self.flight_object.add_wine_and_increment_version(wine_id)
            self.flight_object.ref_id = self.flight_id
            self.flight_object.update()
        return {
            'flightId': self.flight_object.ref_id,
            'flightData': {'currentVersion': self.flight_object.current_version,
                           'wines': self.flight_object.wine_ids,
                           'name': self.flight['name'],
                           'versions': self.flight_object.versions,
                           'owner': owner_id}
        }
