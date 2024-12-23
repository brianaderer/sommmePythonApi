import singleton
import json
from google.cloud import firestore
import time


class Messages:

    def __init__(self):
        self.s = singleton.Singleton()

    def handle_message_meta(self, uid, group_id, message, users):
        users_data = json.loads(users)
        clean_uid = uid.replace('"', '')
        message_object = json.loads(message)
        message_object['timestamp'] = self.s.Messages.generate_timestamp()
        data = {'last_message': message_object}
        clean_group = json.loads(group_id)
        group_str = group_id.replace('"', '')
        success = self.s.Cacher.set_data('group:' + group_str, data, '', False)
        if success:
            self.s.FCM.handle_message_send(user_id=clean_uid, group=clean_group, message=message_object,
                                           users=users_data)
        return success

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

    def create_message(self, group_id, owner_id, content, users, message_type='SHARE', update=False):
        user = self.s.User.get_user_by_id(owner_id)
        if update:
            message_ref = self.s.Firebase.db.collection('groups').document(group_id).collection('messages').document(update)
            data = message_ref.get().to_dict()
            flights = content['flights'] + data['data']['flights']
            tastings = content['tastings'] + data['data']['tastings']
            data = self.generate_content_from_share(content=content, user=user, add_flights=len(data['data']['flights']), add_tastings=len(data['data']['tastings']))
        else:
            flights = content['flights']
            tastings = content['tastings']
            data = self.generate_content_from_share(content=content, user=user)
        message_val = data['message_val']
        message = {
            'type': message_type,
            'value': message_val,
            'timestamp': self.generate_timestamp(),
            'owner': owner_id.replace('"', ''),
            'data': {
                'flights': flights,
                'tastings': tastings,
            }
        }
        if not update:
            doc_ref = self.s.Firebase.db.collection('groups').document(group_id.replace('"', '')).collection(
                'messages').document()
        else:
            doc_ref = message_ref
        if len(message['value']) > 0 and (content['flights'] or content['tastings']):
            doc_ref.set(message)
            str_message = json.dumps(message)
            str_group_id = json.dumps(group_id)
            self.handle_message_meta(uid=owner_id, users=users, message=str_message, group_id=str_group_id)

    def generate_content_from_share(self, content, user, add_flights=0, add_tastings=0):
        string = ''
        name = user['displayName']
        flights_length = len(content['flights']) + add_flights
        tastings_length = len(content['tastings']) + add_tastings
        string = name + ' shared '
        flight_string = flights_length.__str__() + ' ' + (
            'flights' if flights_length > 1 else 'flight') if flights_length else ''
        item_string = tastings_length.__str__() + ' ' + ('tastings' if tastings_length > 1 else 'tasting') if tastings_length else ''
        string += flight_string if flights_length else ''
        string += ' and ' if flights_length and tastings_length else ''
        string += item_string if item_string is not None else ''
        if not flights_length and not tastings_length:
            string = ''
        return {'message_val': string, 'flights': flights_length, 'tastings': tastings_length}

    def generate_timestamp(self):
        # Get the current time in seconds since the epoch
        current_time = time.time()
        # Convert the time to milliseconds and return as an integer
        timestamp = int(current_time * 1000)
        return timestamp
