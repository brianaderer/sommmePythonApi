import json

import singleton as singleton


class User:
    db = None
    first = True

    def __init__(self):
        self.s = singleton.Singleton()
        self.instantiate_firebase()

    def instantiate_firebase(self):
        if self.db is None:
            self.db = self.s.Firebase.db

    def add_space_if_length(self, string):
        space = '  ' if not self.first else ''
        if len(string):
            self.first = False
        return space + string if len(string) else ''

    def create_user_search(self, email, decoded_data):
        self.first = True
        return self.s.Cacher.search_prep(
            self.add_space_if_length(decoded_data['displayName']) + self.add_space_if_length(
                email) + self.add_space_if_length(decoded_data['company']) + self.add_space_if_length(
                decoded_data['country']) + self.add_space_if_length(
                decoded_data['province']) + self.add_space_if_length(decoded_data[
                                                                         'city'])
        )

    def update_user(self, data):
        decoded_data = json.loads(data)
        uid = decoded_data['uid']
        email = decoded_data['email']
        if 'certifications' not in decoded_data:
            decoded_data['certifications'] = []
        if 'displayName' not in decoded_data:
            decoded_data['displayName'] = ''
        if 'jobTitle' not in decoded_data:
            decoded_data['jobTitle'] = ''
        if 'company' not in decoded_data:
            decoded_data['company'] = ''
        if 'preferredEmail' not in decoded_data:
            decoded_data['preferredEmail'] = email
        if 'role' not in decoded_data:
            decoded_data['role'] = ''
        if 'country' not in decoded_data:
            decoded_data['country'] = ''
        if 'province' not in decoded_data:
            decoded_data['province'] = ''
        if 'city' not in decoded_data:
            decoded_data['city'] = ''
        if 'searchable' not in decoded_data:
            decoded_data['searchable'] = True
        if 'addSalutations' not in decoded_data:
            decoded_data['addSalutations'] = True
        document_data = {
            'searchText': self.create_user_search(email, decoded_data),
            'preferredEmail': decoded_data['preferredEmail'],
            'company': decoded_data['company'],
            'jobTitle': decoded_data['jobTitle'],
            'certifications': decoded_data['certifications'],
            'country': decoded_data['country'],
            'province': decoded_data['province'],
            'city': decoded_data['city'],
            'role': decoded_data['role'],
            'searchable': decoded_data['searchable'],
            'addSalutations': decoded_data['addSalutations'],
            'displayName': decoded_data['displayName'],
        }
        return self.db.collection('users').document(uid).set(document_data)
