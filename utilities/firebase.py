import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import singleton


class Firebase:
    # Application Default credentials are automatically created.

    def __init__(self):
        self.cred = credentials.Certificate("private/serviceAccountKey.json")
        firebase_admin.initialize_app(self.cred)
        self.db = firestore.client()
        self.s = singleton.Singleton()
