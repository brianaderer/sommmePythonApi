import singleton


class Crons:
    def __init__(self):
        self.s = singleton.Singleton()

    def update_caches(self):
        self.s.Query.update_producers_cache()
        self.s.Query.update_users_cache()
        self.s.Query.update_sub_caches()
