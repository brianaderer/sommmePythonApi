import singleton


class UserType:
    uid = None
    email = None
    value = None
    preferredEmail = None
    company = None
    jobTitle = None
    certifications = None
    country = None
    province = None
    city = None
    role = None
    searchable = None
    addSalutations = None
    displayName = None
    screenName = None
    firstName = None
    lastName = None
    decoded_data = None

    def __init__(self, decoded_data: dict):
        self.first = None
        self.s = singleton.Singleton()
        self.decoded_data = self.sanitize_decoded_data(decoded_data)
        self.convert_decoded_to_object()

    def sanitize_decoded_data(self, decoded_data: dict) -> dict:
        if 'certifications' not in decoded_data:
            decoded_data['certifications'] = []
        if 'displayName' not in decoded_data:
            decoded_data['displayName'] = ''
        if 'jobTitle' not in decoded_data:
            decoded_data['jobTitle'] = ''
        if 'company' not in decoded_data:
            decoded_data['company'] = ''
        if 'preferredEmail' not in decoded_data:
            decoded_data['preferredEmail'] = self.email
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
        if 'screenName' not in decoded_data:
            decoded_data['screenName'] = ''
        if 'firstName' not in decoded_data:
            decoded_data['firstName'] = ''
        if 'lastName' not in decoded_data:
            decoded_data['lastName'] = ''
        if 'addSalutations' not in decoded_data:
            decoded_data['addSalutations'] = True
        decoded_data['value'] = self.create_user_search(decoded_data['preferredEmail'], decoded_data)
        return decoded_data

    def add_space_if_length(self, string):
        space = '  ' if not self.first else ''
        if len(string):
            self.first = False
        return space + string if len(string) else ''

    def create_user_search(self, email, decoded_data):
        self.first = True
        return self.add_space_if_length(decoded_data['displayName']) + self.add_space_if_length(
            email) + self.add_space_if_length(decoded_data['company']) + self.add_space_if_length(
            decoded_data['country']) + self.add_space_if_length(
            decoded_data['province']) + self.add_space_if_length(decoded_data[
                                                                     'city']) + self.add_space_if_length(decoded_data[
                                                                                                             'screenName'])

    def convert_decoded_to_object(self):
        for key, value in self.decoded_data.items():
            setattr(self, key, value)

    def return_data(self):
        data = self.__dict__.copy()
        data.pop('s', None)
        data.pop('decoded_data', None)
        return data
