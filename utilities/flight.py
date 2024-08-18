import singleton as singleton
import time


class Flight:

    def __init__(self):
        self.s = singleton.Singleton()
        self.flight_ref = self.s.Save.flights

    def create_flight(self, wines, owner_id, name, flights, response):
        indices = list(range(len(wines)))
        flight = {
            'wines': wines,
            'owner': owner_id,
            'timestamp': int(time.time()),
            'name': name,
            'versions': {'1': indices},
            'currentVersion': 1,
        }
        doc_ref = flights.document()
        doc_ref.set(flight)
        return response.update({'flight_id': doc_ref.id})

    def update_flight(self, wine_id, owner_id, flight_id):
        doc_ref = self.flight_ref.document(flight_id)
        doc = doc_ref.get()
        current_flight = doc.to_dict()
        wines = current_flight['wines']
        if wine_id not in wines:
            wines.append(wine_id)
            wine_idx = len(wines) - 1
            flight_idx = str(current_flight['currentVersion'])
            versions = current_flight['versions']
            current_flight_list = versions[str(current_flight['currentVersion'])].copy()
            current_flight_list.append(wine_idx)
            new_flight_idx = str(int(flight_idx) + 1)
            versions[new_flight_idx] = current_flight_list
            current_flight['versions'] = versions
            current_flight['currentVersion'] = int(new_flight_idx)
            doc_ref.update(current_flight)
