import singleton as singleton
import redis
import time


class Cacher:
    PRODUCER_LOCK = 'producer_lock'

    def __init__(self):
        self.s = singleton.Singleton()
        self.r = redis.Redis(host='localhost', port=6379, decode_responses=True)

    # timeout in seconds
    def ensure_json_key(self, key, json_key=None, timeout=10):
        # Attempt to acquire the lock
        if not self.lock_or_unlock(True, timeout):
            raise TimeoutError("Failed to acquire lock within the specified timeout period.")

        try:
            # Check if the key exists
            data = self.r.json().get(key, '$')
            if data is None:
                data_dict = {}
            else:
                data_dict = data[0]

            if json_key is not None and json_key not in data_dict:
                data_dict[json_key] = {}
                self.r.json().set(key, '$', data_dict)

            return data_dict
        finally:
            # Release the lock
            self.lock_or_unlock(False)

    def check_if_key_exists(self, key):
        return self.r.exists(key)

    def lock_or_unlock(self, lock, timeout=10):
        if lock:
            start_time = time.time()
            while time.time() - start_time < timeout:
                # Try to set the lock (set if not exists)
                if self.r.set(self.PRODUCER_LOCK, '1', nx=True):
                    return True
                time.sleep(0.1)  # Sleep for a short period before retrying
            return False  # Failed to acquire the lock within the timeout period
        else:
            # Delete the lock
            return self.r.delete(self.PRODUCER_LOCK)

    def retrieve_cached_object(self, key):
        return self.ensure_json_key(key=key)

    def set_data(self, key, data):
        result = self.r.json().set(name=key, path='$', obj=data)
        self.r.expire(key,
                      3 * 60 * 60)  # Set expiration time to 3 hours (3 hours * 60 minutes/hour * 60 seconds/minute)
        return result
