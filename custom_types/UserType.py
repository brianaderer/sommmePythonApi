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
    device_ids = None

    def __init__(self, decoded_data: dict, key: str):
        self.first = None
        self.uid = key
        self.s = singleton.Singleton()
        self.decoded_data = self.sanitize_decoded_data(decoded_data)
        self.email = decoded_data['email'] if 'email' in decoded_data else ''
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
        if 'device_ids' not in decoded_data:
            decoded_data['device_ids'] = []
        decoded_data['value'] = self.create_user_search(decoded_data['preferredEmail'], decoded_data)
        if len(decoded_data['firstName']) and len(decoded_data['lastName']):
            decoded_data['displayName'] = decoded_data['firstName'] + ' ' + decoded_data['lastName']
        return decoded_data

    def add_space_if_length(self, string):
        if string is not None:
            space = '  ' if not self.first else ''
            if len(string):
                self.first = False
            return space + string if len(string) else ''
        else:
            return ''

    def create_user_search(self, email, decoded_data):
        self.first = True
        name = decoded_data['firstName'] + ' ' + decoded_data['lastName'] if (
                                                                                         'firstName' and 'lastName' in decoded_data) and len(
            decoded_data['firstName']) and len(decoded_data['lastName']) else decoded_data['displayName']
        return self.add_space_if_length(name) + self.add_space_if_length(
            email) + self.add_space_if_length(decoded_data['company']) + self.add_space_if_length(
            decoded_data['country']) + self.add_space_if_length(
            decoded_data['province']) + self.add_space_if_length(decoded_data[
                                                                     'city']) + self.add_space_if_length(
            decoded_data['screenName'])

    def add_device(self, device_id):
        if device_id not in self.device_ids:
            self.device_ids.append(device_id)

    def delete_device(self, device_id):
        print(self.device_ids)
        self.device_ids.remove(device_id)
        print(self.device_ids)

    def get_device_ids(self):
        return self.device_ids

    def get_initials(self):
        return_str = ''
        str_list = self.displayName.split(' ')
        for item in str_list:
            return_str += item[0]
        return return_str

    def get_user_name(self):
        first_and_last = self.firstName + ' ' + self.lastName
        display_name = self.displayName
        return display_name

    def convert_decoded_to_object(self):
        for key, value in self.decoded_data.items():
            setattr(self, key, value)

    def return_data(self):
        data = self.__dict__.copy()
        data.pop('s', None)
        data.pop('decoded_data', None)
        return data
