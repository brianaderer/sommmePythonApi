import singleton


class CuveeType:

    def __init__(self, cuvee):
        self.s = singleton.Singleton()
        key = self.s.Query.get_key(cuvee)
        value = cuvee[key]
        self.value = value['value']
        self.db_id = key
        self.appellations = []
        self.colors = []
        self.owners = value['owners']

    def return_data(self) -> dict:
        data = self.__dict__.copy()
        data.pop('s', None)
        return data
