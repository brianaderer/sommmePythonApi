import singleton


class UserType:

    def __init__(self, decoded_data: dict):
        decoded_data = self.sanitize_decoded_data(decoded_data)
        self.s = singleton.Singleton()
        self.uid = decoded_data['uid']
        self.email = decoded_data['email']
        self.searchText = self.s.User.create_user_search(decoded_data['preferredEmail'], decoded_data)
        self.preferredEmail = decoded_data['preferredEmail']
        self.company = decoded_data['company']
        self.jobTitle = decoded_data['jobTitle']
        self.certifications = decoded_data['certifications']
        self.country = decoded_data['country']
        self.province = decoded_data['province']
        self.city = decoded_data['city']
        self.role = decoded_data['role']
        self.searchable = decoded_data['searchable']
        self.addSalutations = decoded_data['addSalutations']
        self.displayName = decoded_data['displayName']
        self.screenName = decoded_data['screenName']
        self.firstName = decoded_data['firstName']
        self.lastName = decoded_data['lastName']

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
        return decoded_data
