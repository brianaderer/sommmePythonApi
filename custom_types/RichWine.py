import singleton
from custom_types.Error import Error
from custom_types.LongformItem import LongformItem


class RichWine:
    def __init__(self, wine: 'Wine', owner):
        self.full_title = None
        self.s = singleton.Singleton()
        self.reset(wine)
        self.owner = owner
        self.props_ref = self.s.Firebase.db.collection('properties').document('items')
        # print('___________')
        # print(wine.full_title)
        # check all the uploaded props
        for key in wine.keys:
            if not isinstance(self[key], list):
                self[key] = []
            # print('___KEY: ' + key)
            if key in self.s.Dependencies.return_dep_list():
                has_all_deps = True
                dep_keys = self.s.Dependencies.dependencies[key]
                for dep_key in dep_keys:
                    if not len(wine.get(dep_key)):
                        has_all_deps = False
                if has_all_deps:
                    try:
                        props = self.s.Props.get_or_create_term(key, wine.get(key), self.owner)
                        # print(props)
                        self[key].append(LongformItem(props[0]))
                    except Exception as e:
                        self[key].append(Error(e.__str__()))
                else:
                    self[key].append(Error('Could not find necessary dependencies'))
            else:
                try:
                    props = self.s.Props.get_or_create_term(key, wine.get(key), self.owner)
                    self[key].append(LongformItem(props[0]))
                except Exception as e:
                    self[key].append(Error(e.__str__()))

    def reset(self, wine: 'Wine'):
        self.full_title = wine.full_title
        for key in wine.keys:
            self[key] = []

    def __setitem__(self, key, value):
        self.__dict__[key] = value

    def get(self, key) -> LongformItem | None:
        try:
            return getattr(self, key, None)
        except Exception as e:
            return None

    def __getitem__(self, item):
        return self.__dict__.get(item)

    def recurse_terms(self):
        pass
        for key in self.s.Dependencies.correlations:
            data = self.get(key)
            for datum in data:
                if not isinstance(datum, Error):
                    cache_string = key + ':' + datum.key
                    correlations = self.s.Dependencies.correlations[key]
                    for corr in correlations:
                        results = self.s.Cacher.get_data(cache_string)
                        term_object = LongformItem((datum.key, results[0]))
                        if not isinstance(term_object, Error):
                            corr_results = self.get(corr)
                            if corr_results is not None and not isinstance(corr_results, Error):
                                for result in corr_results:
                                    append = False
                                    write_data = term_object.data.copy()
                                    if corr not in write_data:
                                        write_data[corr] = []
                                    if not isinstance(result, Error) and result is not None:
                                        data_object = {result.key: result.get_value()}
                                        if data_object not in write_data[corr]:
                                            append = True
                                            write_data[corr].append(data_object)
                                    if append:
                                        self.s.Props.update_term(coll=key, key=datum.key, data=write_data)
