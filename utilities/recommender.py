import json

import singleton as singleton


class Recommender:
    def __init__(self):
        self.s = singleton.Singleton()

    def get_recommendation(self, class_name, text, deps='[]'):
        deps = json.loads(deps)
        print(deps)
        results = self.s.Cacher.get_collection(class_name=class_name)
        coll = self.s.Query.parse_redis_search_value(data=results)
        search_text = self.s.Cacher.search_prep(text)
        filtered_class_name = class_name.replace('"', '')

        for d in coll:
            key = self.s.Query.get_key(d)
            item = d[key]
            d_search_text = item['search_text']
            d[key]['similarity'] = self.s.Similarity.elastic_sim(search_text, d_search_text)

        # Sort the array by similarity scores in descending order
        sorted_array = sorted(coll, key=lambda x: x[self.s.Query.get_key(x)]['similarity'], reverse=False)
        top_10 = sorted_array[:100]
        filtered_array = [{self.s.Query.get_key(item).replace(filtered_class_name + ':', ''): item[self.s.Query.get_key(item)]}for item in top_10]
        return filtered_array
