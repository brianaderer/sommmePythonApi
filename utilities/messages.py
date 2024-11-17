import singleton
from google.cloud import firestore
import time


class Messages:

    def __init__(self):
        self.s = singleton.Singleton()

    def get_most_recent_message(self, group_id):
        messages_ref = self.s.Firebase.db.collection('groups').document(group_id).collection('messages')
        query = messages_ref.order_by('timestamp', direction=firestore.Query.DESCENDING).limit(1)
        results = query.get()

        if results:  # Check if results are not empty
            most_recent_message = results[0].to_dict()
            message_id = results[0].id
        else:
            most_recent_message = None
            message_id = None

        return {'message': most_recent_message, 'message_id': message_id}

    def create_message(self, group_id, owner_id, content, key, message_type='SHARE', update=False):
        user = self.s.User.get_user_by_id(owner_id)
        if update:
            message_ref = self.s.Firebase.db.collection('groups').document(group_id).collection('messages').document(update)
            data = message_ref.get().to_dict()
            headers = content['headers'] + data['data']['flights']
            items = content['items'] + data['data']['tastings']
            data = self.generate_content_from_share(content=content, user=user, key=key, add_headers=len(data['data']['flights']), add_items=len(data['data']['tastings']) )
        else:
            headers = content['headers']
            items = content['items']
            data = self.generate_content_from_share(content=content, user=user, key=key)
        message_val = data['message_val']
        message = {
            'type': message_type,
            'value': message_val,
            'timestamp': self.generate_timestamp(),
            'owner': owner_id.replace('"', ''),
            'data': {
                'flights': headers,
                'tastings': items,
            }
        }
        if not update:
            doc_ref = self.s.Firebase.db.collection('groups').document(group_id.replace('"', '')).collection(
                'messages').document()
        else:
            doc_ref = message_ref
        doc_ref.set(message)
        self.s.Cacher.set_data('group:' + group_id, {'last_message': message})

    def generate_content_from_share(self, content, user, key, add_headers=0, add_items=0):
        string = ''
        name = user['displayName']
        header_length = len(content['headers']) + add_headers
        item_length = len(content['items']) + add_items
        header_key = key['headers']
        item_key = key['items']
        header_string = header_length.__str__() + ' ' + (
            header_key if header_length > 1 else header_key[:-1]) if header_length else None
        item_string = item_length.__str__() + ' ' + (item_key if item_length > 1 else item_key[:-1]) if item_length else None
        string += name + ' shared ' + header_string if header_string is not None else ''
        string += ' and ' if header_length and item_length else ''
        string += item_string if item_string is not None else ''
        return {'message_val': string, 'headers': header_length, 'items': item_length}

    def generate_timestamp(self):
        # Get the current time in seconds since the epoch
        current_time = time.time()
        # Convert the time to milliseconds and return as an integer
        timestamp = int(current_time * 1000)
        return timestamp

