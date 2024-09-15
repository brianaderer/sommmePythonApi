import singleton
from custom_types.ShortformItem import ShortformItem
from typing import List


class LongformItem:
    excludes = [
        'search_text',
        'owners',
        'value'
    ]

    def __init__(self, data: tuple | None):
        self.s = singleton.Singleton()
        self.reset()
        if data is not None:
            self.key = data[0]
            self.data = data[1]
            self.owner = data[1]['owners']
            self.search_text = data[1]['search_text']

    def reset(self):
        self.owner = None
        self.search_text = None
        self.key = None
        self.data = None

    def get_keys(self):
        keys = []
        for key in list(self.data.keys()):
            if key not in self.excludes:
                keys.append(key)
        return keys

    def get_value(self):
        if 'value' in self.data:
            return self.data['value']
        else:
            return None

    def get_id_dict(self):
        return {self.key: self.get_value()}
    def check_dep(self, key, value: ShortformItem):
        return (key in self.data and
                value.is_equal(self.data[key]))

    def get_prop_vals(self, prop) -> List[ShortformItem]:
        return_data: List[ShortformItem] = []
        if prop in self.get_keys():
            items = self.data[prop]
            for item in items:
                return_data.append(ShortformItem(item))
        return return_data

    def get_shortform_dict(self):
        return {self.key: self.get_value()}

    def __setitem__(self, key, value):
        self.__dict__[key] = value

    def __getitem__(self, item):
        return self.__dict__.get(item)
