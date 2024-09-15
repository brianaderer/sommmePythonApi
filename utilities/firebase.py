import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import singleton
from google.cloud.firestore_v1 import FieldFilter
import time


class Firebase:
    # Application Default credentials are automatically created.
    FieldFilter = FieldFilter

    def __init__(self):
        self.cred = credentials.Certificate("private/serviceAccountKey.json")
        firebase_admin.initialize_app(self.cred)
        self.db = firestore.client()
        self.s = singleton.Singleton()

    def acquire_lock(self, coll, lock=True, max_retries=100):
        if lock:
            for _ in range(max_retries):  # Retry up to max_retries times
                set_lock = self.s.Cacher.get_data('firebase:' + coll)
                if set_lock is None or not set_lock[0]:
                    self.s.Cacher.set_data(key='firebase:' + coll, data=True, search=False, expire=20)
                    return True
                else:
                    time.sleep(0.05)
            return False
        else:
            self.s.Cacher.set_data(key='firebase:' + coll, data=False, search=False)
