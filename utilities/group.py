import json
import singleton

from custom_types.UserType import UserType
from custom_types.GroupType import GroupType


class Group:
    request = None

    def __init__(self):
        self.s = singleton.Singleton()
        self.group = GroupType()

    def reset(self):
        self.group = GroupType.__new__(GroupType)
        self.group.__init__()
        self.request = None

    def create_group(self, data, owner):
        self.reset()
        self.group.owner = owner
        rendered_data = json.loads(data)
        for user in rendered_data:
            key = list(user.keys())[0]
            value = user[key]
            user_object = UserType(decoded_data=value, key=key)
            self.group.add_user(user=user_object)
        self.request = self.group.generate_request()
        return self.process_group_request()

    def process_group_request(self):
        group_ref = self.s.Firebase.db.collection('groups')
        docs = (
            group_ref.where(filter=self.s.Firebase.FieldFilter('users', '==', self.request['users']))
            .stream()
        )
        for doc in docs:
            return doc.ref_id
        result = self.s.Firebase.db.collection('groups').add(self.request)
        return result[1].ref_id
