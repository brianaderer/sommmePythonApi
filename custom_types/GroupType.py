import singleton
from custom_types.UserType import UserType


class GroupType:
    users: list[UserType] = []
    owner: str | None = None

    def __new__(cls, *args, **kwargs):
        return super().__new__(cls)

    def __init__(self):
        self.users = []
        self.owner = None
        self.s = singleton.Singleton()


    def add_user(self, user: UserType):
        self.users.append(user)

    def generate_request(self) -> dict:
        owner_string = self.owner.replace('"', '')
        owner_ref = self.s.Firebase.db.collection('users').document(owner_string).get()
        self.add_user(UserType(decoded_data=owner_ref.to_dict(), key=owner_string))
        self.owner = owner_string
        title = ''
        users_list = []
        accepted_list = []
        for user in self.users:
            user_id = user.uid
            accepted = user.uid == owner_string
            users_list.append(user_id)
            title += user.displayName if len(user.displayName) else user.firstName + ' ' + user.lastName
            title += ', '
            if accepted:
                accepted_list.append(user_id)
        trimmed_title = title[:-2]
        return {'users': users_list, 'accepted': accepted_list, 'name': trimmed_title, 'owner': owner_string, 'options': {}}
