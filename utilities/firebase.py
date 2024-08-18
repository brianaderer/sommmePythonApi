import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import singleton
from google.cloud.firestore_v1 import FieldFilter



class Firebase:
    # Application Default credentials are automatically created.
    FieldFilter = FieldFilter

    def __init__(self):
        self.cred = credentials.Certificate("private/serviceAccountKey.json")
        firebase_admin.initialize_app(self.cred)
        self.db = firestore.client()
        self.s = singleton.Singleton()

    def save_attribute(self, coll, data, key):
        print(coll)
        print(key)
        print(data)