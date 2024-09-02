import json

import singleton as singleton
from custom_types.UserType import UserType


class User:
    db = None
    first = True
    userResults = []

    def __init__(self):
        self.s = singleton.Singleton()
        self.instantiate_firebase()

    def instantiate_firebase(self):
        if self.db is None:
            self.db = self.s.Firebase.db

    def search_for_user(self, data: str) -> list:
        self.userResults = []
        search_text = json.loads(data)
        results = self.s.Cacher.key_search(value=search_text, key='users')
        return self.s.Query.parse_redis_search_value(results)

    def update_user(self, data: str) -> dict:
        decoded_data = json.loads(data)
        uid = decoded_data['uid']
        user = UserType(decoded_data=decoded_data, key=uid)
        document_data = user.return_data()
        self.s.Cacher.set_data('users:' + uid, document_data)
        return self.db.collection('users').document(uid).set(document_data)
