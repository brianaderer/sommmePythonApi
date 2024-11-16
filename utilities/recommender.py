import json

import singleton as singleton


class Recommender:
    def __init__(self):
        self.s = singleton.Singleton()

    def get_recommendation(self, class_name, text, deps='[]'):
        try:
            deps = json.loads(deps)
        except (ValueError, TypeError):
            deps = []
        results = self.s.Cacher.get_collection(class_name=class_name)
        coll = self.s.Query.parse_redis_search_value(data=results)
        search_text = self.s.Cacher.search_prep(text)
        filtered_class_name = class_name.replace('"', '')
        filtered_coll = []
        found_deps = {}
        for d in coll:
            add_to_filtered = False
            key = self.s.Query.get_key(d)
            item = d[key]
            for dep in deps:
                if not len(dep):
                    break
                dep_key = self.s.Query.get_key(dep)
                wine_val = dep[dep_key]
                wine_key = self.s.Query.get_key(wine_val)
                if dep_key in item:
                    keyed_item = item[dep_key][0]
                    search_val = self.s.Cacher.search_prep(keyed_item[self.s.Query.get_key(keyed_item)])
                    wine_search_text = wine_val[wine_key]['search_text'] if 'search_text' in wine_val[wine_key] else ''
                    found_deps[dep_key] = wine_search_text
                    if search_val == wine_search_text:
                        add_to_filtered = True
                        break

            d_search_text = item['search_text']
            d[key]['similarity'] = self.s.Similarity.elastic_sim(search_text, d_search_text)
            if add_to_filtered:
                filtered_coll.append(d)

        return_array = filtered_coll + coll
        result = []
        for i in return_array:
            if i not in result:
                result.append(i)
        # Sort the array by similarity scores in descending order
        sorted_array = sorted(result, key=lambda x: x[self.s.Query.get_key(x)]['similarity'], reverse=False)
        top_100 = sorted_array[:100]
        filtered_array = [{self.s.Query.get_key(item).replace(filtered_class_name + ':', ''): item[self.s.Query.get_key(item)]}for item in top_100]
        return_list = []

        if len(found_deps) > 0:
            for item in filtered_array:
                for key in list(found_deps.keys()):
                    if key in list(item.values())[0]:
                        val = list(item.values())[0][key][0]
                        parsed_val = list(val.values())[0]
                        search_val = self.s.Cacher.search_prep(parsed_val)
                        search_against = self.s.Cacher.search_prep(found_deps[key])
                        if search_val == search_against:
                            return_list.append(item)
        else:
            return_list = filtered_array
        return return_list
