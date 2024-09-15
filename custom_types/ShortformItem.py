import singleton


class ShortformItem:

    def __init__(self, data: dict | None):
        self.s = singleton.Singleton()
        if data is not None:
            self.key = list(data.keys())[0]
            self.value = data[self.key]
        else:
            self.key = None
            self.value = None

    def is_equal(self, data: dict | None):
        return (data is not None and
                list(data.keys())[0] == self.key and
                data[list(data.keys())[0]] == self.value)
