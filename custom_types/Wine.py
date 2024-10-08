import re
import singleton
from custom_types.RichWine import RichWine
from custom_types.LongformItem import LongformItem
from custom_types.Error import Error
from typing import AnyStr


class Wine:
    prev_words = {
    }
    identity_keys = [
        'producer',
        'cuvee',
        'vintage'
    ]
    stop_words = {
        'Type': 'types',
        'Producer': 'producers',
        'Region': 'regions',
        'Grapes': 'grapes',
        'Grape': 'grapes',
        'Appellation': 'appellations',
        'Size': 'sizes',
        'SKU': 'skus',
        'Distributor': 'distributors'
    }
    keys = [
        'classes',
        'types',
        'colors',
        'producer',
        'regions',
        'grapes',
        'appellations',
        'sizes',
        'skus',
        'countries',
        'vintage',
        'cuvee',
    ]

    def __init__(self, owner=None):
        self.s = singleton.Singleton()
        self.db_value = None
        self.last_stop_word = None
        self.capture_footer = False
        self.skip_item = True
        self.footer = []
        self.classes = []
        self.types = []
        self.colors = []
        self.producer = []
        self.regions = []
        self.grapes = []
        self.appellations = []
        self.sizes = []
        self.skus = []
        self.countries = []
        self.distributors = []
        self.vintage = []
        self.cuvee = []
        self.phone = ''
        self.email = ''
        self.full_title = ''
        self.orphans = []
        self.notes = ''
        self.data_live = False
        self.id = ''
        self.rich_wine: RichWine | None = None
        self.owner = owner
        self.owner_id = None
        self.ref_id = None

    def initiate_uploaded_wine(self, array):
        index = 0
        for item in array:
            if item in list(self.stop_words.keys()):
                self.last_stop_word = index
            index += 1
        index = 0
        for item in array:
            if self.capture_footer:
                if self.skip_item:
                    self.skip_item = False
                    continue
                else:
                    self.footer.append(item)
                    continue
            if item in list(self.stop_words.keys()):
                stop_here = index == self.last_stop_word
                if not stop_here:
                    data = self.iterate_forward_indices(array, index)
                else:
                    data = array[index + 1]
                    self.capture_footer = True
                method_name = self.stop_words[item] + '_handler'
                method = getattr(self, method_name, None)
                if method:
                    try:
                        method(data)
                    except:
                        print('couldnt get data for ' + item)
            index += 1
        self.full_title = array[0]
        self.parse_full_title()

    def parse_wine_dict(self, wine_dict):

        for key in wine_dict:
            for value in wine_dict[key]:
                val = value[list(value.keys())[0]]
                self[key].append(val['value'])

    def iterate_forward_indices(self, array, index, forward_index=1, return_string=''):
        # Check if index + forward_index is within the bounds of the array
        if (index + forward_index) < len(array):
            if array[index + forward_index] not in list(self.stop_words.keys()):
                return_string += ' ' + array[index + forward_index]
                return self.iterate_forward_indices(array, index, forward_index + 1, return_string)
            else:
                return return_string
        else:
            # If out of bounds, return the accumulated string
            return return_string

    def __getitem__(self, item):
        return getattr(self, item)

    def get(self, key):
        return getattr(self, key, None)

    def grapes_handler(self, grapes_string):
        grapes_array = [grape.strip() for grape in grapes_string.split(',')]
        self.grapes = grapes_array

    def types_handler(self, types_string):
        types_array = [wine_type.strip() for wine_type in types_string.split('-')]
        self.classes.append(types_array[0])
        self.types.append(types_array[1])
        self.colors.append(types_array[2])

    def regions_handler(self, regions_string):
        regions_array = [region.strip() for region in regions_string.split(',')]
        self.regions.append(regions_array[0])
        if len(regions_array) > 1:
            self.countries.append(regions_array[1])

    def producers_handler(self, producers_string):
        self.producer.append(producers_string.strip())

    def cuvees_handler(self, cuvees_string):
        self.cuvee.append(cuvees_string.strip())

    def vintages_handler(self, vintage_value):
        self.vintage.append(str(vintage_value))

    def appellations_handler(self, appellations_string):
        self.appellations.append(appellations_string.strip())

    def distributors_handler(self, distributors_string):
        self.distributors.append(distributors_string.strip())

    def skus_handler(self, skus_string):
        self.skus.append(skus_string.strip())

    def sizes_handler(self, sizes_string):
        self.sizes.append(sizes_string.strip())

    def parse_full_title(self):
        titular_array = self.split_title(self.full_title)
        self.cuvee.append(titular_array[1])
        self.vintage.append(titular_array[2])

    def split_title(self, title):
        matches = re.findall(self.s.P3.title_pattern, title)
        if matches:
            return list(matches[0])  # Convert the tuple to a list
        return []  # Return an empty list if no match is found

    def generate_dict(self):
        wine_dict = {}
        for key in self.keys:
            wine_dict[key] = self.get(key)

    def create_rich_wine(self):
        self.rich_wine = RichWine(self, self.owner)
        self.rich_wine.recurse_terms()

    def create_dict(self):
        try:
            dict_object = {'owners': [self.owner_id, self.owner]}
            producer: LongformItem = self.rich_wine.get('producer')[0]
            producer_dict: LongformItem | Error = producer.get_id_dict()
            cuvee: LongformItem = self.rich_wine.get('cuvee')[0]
            vintage: LongformItem = self.rich_wine.get('vintage')[0]
            cuvee_dict = cuvee.get_id_dict()
            vintage_dict = vintage.get_id_dict()
            dict_object['producer'] = producer_dict
            dict_object['cuvee'] = cuvee_dict
            dict_object['vintage'] = vintage_dict
            for key in [key for key in self.keys if key not in self.identity_keys]:
                data = self.rich_wine.get(key)
                if not isinstance(data, Error):
                    if key not in dict_object:
                        dict_object[key] = []
                    for datum in data:
                        if not isinstance(datum, Error):
                            datum: LongformItem
                            dict_object[key].append(datum.get_shortform_dict())
            return dict_object
        except Exception as e:
            return Error(e.__str__())

    def identify(self) -> AnyStr | bool:
        producer_object: LongformItem = self.rich_wine.get('producer')[0]
        cuvee_object: LongformItem = self.rich_wine.get('cuvee')[0]
        vintage_object: LongformItem = self.rich_wine.get('vintage')[0]
        if not self.s.Save.is_error(cuvee_object) and not self.s.Save.is_error(
                cuvee_object) and not self.s.Save.is_error(vintage_object):
            producer = producer_object.get_shortform_dict()
            cuvee = cuvee_object.get_shortform_dict()
            vintage = vintage_object.get_shortform_dict()
            producer_filter = self.s.Firebase.FieldFilter('producer', '==', producer)
            cuvee_filter = self.s.Firebase.FieldFilter('cuvee', '==', cuvee)
            vintage_filter = self.s.Firebase.FieldFilter('vintage', '==', vintage)
            coll_ref = self.s.Firebase.db.collection('beverages')
            docs = (coll_ref
                    .where(filter=producer_filter)
                    .where(filter=cuvee_filter)
                    .where(filter=vintage_filter)
                    .stream()
                    )
            first_doc = next(docs, None)
            if first_doc is not None:
                self.db_value = first_doc.to_dict()
            return first_doc.id if first_doc is not None else False
        else:
            return False

    def create(self):
        dict_object = self.create_dict()
        if not isinstance(dict_object, Error):
            coll_ref = self.s.Firebase.db.collection('beverages')
            doc_ref = coll_ref.document()
            doc_ref.set(dict_object)
            self.create_notes(doc_ref.id)
            return doc_ref.id
        else:
            return None

    def create_notes(self, beverage_id):
        if len(self.notes):
            doc_ref = self.s.Firebase.db.collection('notes').document()
            data = {'value': self.notes, 'owner': self.owner_id, 'wineId': beverage_id}
            doc_ref.set(data)
