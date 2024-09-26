import singleton
from custom_types.Wine import Wine
from custom_types.Error import Error
from custom_types.RichWine import RichWine
from typing import List, AnyStr
import re
import time


class Flight:
    phone_pattern = r"(\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4})"
    email_pattern = r"([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)"
    lookups = {
        'current_version': 'currentVersion'
    }
    appends = ['wine_ids', 'versions']

    def __init__(self, owner=None):
        self.s = singleton.Singleton()
        self.title = None
        self.sales_rep: AnyStr | None = None
        self.rep_title: AnyStr | None = None
        self.rep_phone: AnyStr | None | Error = None
        self.rep_email: AnyStr | None | Error = None
        self.wines: List[Wine] = []
        self.rich_wine: List[RichWine] = []
        self.distributor: AnyStr | None | Error = None
        self.owner = owner
        self.ref_id = None
        self.owner_id = None
        self.wine_ids = []
        self.versions: dict = {}
        self.current_version = 1

    def append_wine(self, wine: Wine, owner_id: AnyStr):
        wine.owner_id = owner_id
        self.wines.append(wine)

    def add_wine_and_increment_version(self, wine_id: AnyStr):
        self.wine_ids.append(wine_id)
        self.current_version += 1
        self.make_wine_id_list()
        self.versions[str(self.current_version)] = (self.get_list_indices(self.wine_ids))

    def make_wine_id_list(self):
        wine_ids = []
        for wine in self.wines:
            if wine.ref_id is not None:
                wine_ids.append(wine.ref_id)
        self.wine_ids = wine_ids

    def list_indices(self, input_list):
        return list(range(len(input_list)))

    def update(self):
        self.make_wine_id_list()
        update_dict = {'wines': [], 'versions': self['versions'], 'currentVersion': int(self.current_version)}
        update_dict['versions'][str(self.current_version)] = self.list_indices(self.wine_ids)
        update_dict['wines'] = self.wine_ids
        doc_ref = self.s.Firebase.db.collection('flights').document(self.ref_id)
        doc_ref.update(update_dict)

    def filter_array(self, array):
        # List of terms to exclude
        exclude_terms = [self.sales_rep, self.rep_title, self.rep_email, self.rep_phone, self.distributor]

        # Filter out any terms that are in the exclude_terms list
        filtered_array = [item for item in array if item not in exclude_terms]
        return filtered_array

    def __getitem__(self, item):
        return getattr(self, item)

    def pre_flight(self):
        index = 0
        for wine in self.wines:
            index += 1
            if len(wine.distributors) > 0:
                if self.distributor is None:
                    self.distributor = wine.distributors[0]
                elif self.distributor != wine.distributors[0]:
                    self.distributor = Error('We found conflicting distributor information')
            footer_index = 0
            wine.footer = [item for item in wine.footer if item.strip()]
            orphans = []
            for text in wine.footer:
                footer_index += 1
                if text == self.distributor:
                    continue
                phones = re.findall(self.phone_pattern, text)
                emails = re.findall(self.email_pattern, text)
                processed = False
                if len(phones) > 0:
                    processed = True
                    if self.rep_phone is None:
                        self.rep_phone = phones[0]
                    elif self.rep_phone != phones[0]:
                        self.rep_phone = Error('We found a phone number mismatch for this flight')
                if len(emails) > 0:
                    processed = True
                    if self.rep_email is None:
                        self.rep_email = emails[0]
                    elif self.rep_email != emails[0]:
                        self.rep_email = Error('We found an email mismatch for this flight')
                if not processed:
                    orphans.append(text)
                if index == len(self.wines):
                    if footer_index == len(wine.footer):
                        if len(orphans) > 0 and self.distributor is None:
                            distributor = orphans.pop().strip()
                            if self.distributor is None:
                                self.distributor = distributor
                        if len(orphans) > 1:
                            self.rep_title = orphans.pop().strip()
                            self.sales_rep = orphans.pop().strip()
            wine.orphans = orphans

    def parse_orphans(self):
        for wine in self.wines:
            wine.notes = ' '.join(self.filter_array(wine.orphans))

    def set_title(self, string):
        parsed_string = string.replace('.pdf', '')
        self.title = self.title_case(parsed_string)

    def title_case(self, sentence):
        # This function uses regular expressions to find words and capitalize them
        return re.sub(r"[A-Za-z]+('[A-Za-z]+)?",
                      lambda mo: mo.group(0)[0].upper() + mo.group(0)[1:].lower(),
                      sentence)

    def get_list_indices(self, input_list):
        return list(range(len(input_list)))

    def create_flight(self):
        flight_dict = {}
        self.make_wine_id_list()
        flight_dict['wines'] = self.wine_ids
        flight_dict['versions'] = {'1': self.get_list_indices(self.wine_ids)}
        flight_dict['currentVersion'] = 1
        flight_dict['owner'] = self.owner_id
        flight_dict['name'] = self.title
        flight_dict['distributorName'] = self.distributor
        flight_dict['rep_contact'] = {'phone': self.rep_phone, 'email': self.rep_email, 'title': self.rep_title,
                                      'name': self.sales_rep}
        flight_dict['timestamp'] = time.time()
        doc_ref = self.s.Firebase.db.collection('flights').document()
        self.ref_id = doc_ref.id
        doc_ref.set(flight_dict)
        return doc_ref.id
