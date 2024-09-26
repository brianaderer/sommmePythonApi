# created_cuvee_object = self.create_cuvee_object(cuvee=filter_cuvee)
# cuvee_key = self.get_key(created_cuvee_object)
# producer_dict, parsed_cuvee, parsed_vintage = self.parse_incoming_suggestions(producer=producer,
#                                                                               cuvee=filter_cuvee,
#                                                                               vintage=vintage)
# parsed_producer = producer_dict[self.get_key(producer_dict)]
# if parsed_producer is None:
#     possible_producers = self.return_coll('producers')
# else:
#     string = parsed_producer['value']
#     possible_producers = self.get_producers(filter_value=string, with_keys=True)
# for producer in possible_producers:
#     key = self.get_key(producer)
#     data = producer[key]
#     self.add_to_suggestions(coll='producers', data=data, key=key)
#     filter_text = '' if parsed_cuvee is None else parsed_cuvee['value']
#     producer_val = producer[key]
#     self.filter_cuvees(cuvees=producer_val['cuvees'], filter_text=unidecode(filter_text))
# if len(possible_producers) == 1:
#     producer_cuvees = possible_producers[0][self.get_key(possible_producers[0])]['cuvees']
#     self.filtered_cuvees = [cuvee for cuvee in producer_cuvees if self.get_key(cuvee) == cuvee_key]
# action_cuvees = self.filtered_cuvees if len(self.filtered_cuvees) else self.all_cuvees
# if len(action_cuvees) == 1:
#     # if False:
#     cuvee = action_cuvees[0]
#     found_wine = self.check_wine(cuvee=cuvee)
#     print(found_wine)
#     wine = self.filter_keys(found_wine[0])
#     modified_wine = self.expand_wine(wine)
#     self.suggestions = modified_wine
#
# else:
#     for cuvee in action_cuvees:
#         key = self.get_key(cuvee)
#         returned_cuvee = self.cache_key_handler(key=key, collection='cuvees')
#         self.add_to_suggestions(coll='cuvees', data=returned_cuvee, key=key)
#         if 'appellations' in returned_cuvee.keys():
#             for appellation in returned_cuvee['appellations']:
#
#                 key = self.get_key(appellation)
#                 returned_appellation = self.cache_key_handler(key=key, collection='appellations')
#                 self.add_to_suggestions(coll='appellations', data=returned_appellation, key=key)
#                 if 'regions' in returned_appellation:
#                     regions = (returned_appellation['regions'])
#                     for region in regions:
#
#                         key = self.get_key(region)
#                         returned_region = self.cache_key_handler(key=key, collection='regions')
#                         self.add_to_suggestions(coll='regions', data=returned_region, key=key)
#                         if 'countries' in returned_region:
#                             countries = returned_region['countries']
#                             for country in countries:
#                                 key = self.get_key(country)
#                                 returned_country = self.cache_key_handler(key=key,
#                                                                           collection='countries')
#                                 self.add_to_suggestions(coll='countries', data=returned_country, key=key,
#                                                         )
#         if 'colors' in returned_cuvee.keys():
#             for color in returned_cuvee['colors']:
#
#                 key = self.get_key(color)
#                 returned_color = self.cache_key_handler(key=key, collection='colors')
#                 self.add_to_suggestions(coll='colors', data=returned_color, key=key)
#                 if 'types' in returned_color:
#                     types = returned_color['types']
#                     for local_type in types:
#
#                         key = self.get_key(local_type)
#                         returned_type = self.cache_key_handler(key=key, collection='types')
#                         self.add_to_suggestions(coll='types', data=returned_type, key=key)
#                         if 'classes' in returned_type:
#                             classes = returned_type['classes']
#                             for class_object in classes:
#                                 key = self.get_key(class_object)
#                                 returned_class = self.cache_key_handler(key=key, collection='classes')
#                                 self.add_to_suggestions(coll='classes', data=returned_class, key=key)
#
# insert_cuvee = True
#
# for cuvee in self.suggestions['cuvees']:
#     if self.get_key(cuvee) == self.get_key(created_cuvee_object):
#         insert_cuvee = False
#         break
#
# if insert_cuvee:
#     self.suggestions['cuvees'].insert(0, created_cuvee_object)
#
# insert_producer = True
#
# for producer in self.suggestions['producers']:
#     val = producer[self.get_key(producer)]['value']
#     if val == producer_dict[self.get_key(producer_dict)]['value']:
#         insert_producer = False
#         break
#
# if insert_producer:
#     self.suggestions['producers'].insert(0, producer_dict)
#
# for key in list(self.suggestions.keys()):
#     if key not in self.excluded_indices and (not self.suggestions[key] or not len(self.suggestions[key])):
#         data = self.s.Cacher.key_search(value='', key=key, limit=False)
#
#         parsed_data = self.parse_redis_search_value(data)
#         self.suggestions[key] = parsed_data
#
# parsed_vintage = self.get_vintage(vintage=vintage)
# self.suggestions['found_wine'] = self.found_wine
# self.suggestions['vintage'] = parsed_vintage
# return self.suggestions