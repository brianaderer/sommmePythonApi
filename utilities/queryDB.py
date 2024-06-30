import singleton as singleton


class Query:
    props=None
    def __init__(self):
        self.s = singleton.Singleton()
        self.instantiate_firebase()
    def instantiate_firebase(self):
        if self.props is None:
            db = self.s.Firebase.db
            self.props = db.collection('properties')

    def get_producers(self, filter_value):
        cached_producers = self.s.Cacher.ensure_json_key('producers')
        if len(cached_producers) > 0:
            producer_data = cached_producers
        else:
            collection = self.props.document('items').collection('producers')
            producers = collection.get()
            producer_data = [producer.to_dict() for producer in producers]
            self.s.Cacher.set_data(key='producers', data=producer_data)

        filtered_producers = [
                                 producer for producer in producer_data
                                 if filter_value.lower() in producer['value'].lower()
                             ][:10]
        return filtered_producers