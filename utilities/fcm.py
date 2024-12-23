import singleton
from custom_types.FCMMessage import FCMMessage
from custom_types.UserType import UserType


class FCM:

    def __init__(self):
        self.s = singleton.Singleton()

    def handle_message_send(self, user_id, message, users, group):
        subscribed_users = [item for item in users if item != user_id]
        clean_user_id = user_id.replace('"', '')
        orig_user = self.s.Cacher.get_data('users:' + clean_user_id)
        orig_user_object = UserType(decoded_data=orig_user[0], key=user_id)
        from_name = orig_user_object.get_user_name()
        title = f"BevNote from {from_name}"
        message_content = message['value']
        body = message_content
        for user in subscribed_users:
            data = self.s.Cacher.get_data('users:' + user)
            user_data = UserType(decoded_data=data[0], key=user)
            for device in user_data.get_device_ids():
                message_object = FCMMessage(device)
                message_object.set_notification(title, body)
                message_object.set_data({'group': group, 'type': 'message'})
                message_object.send_message()

    def handle_device(self, user_id, device_id, action):
        user_data = self.s.Cacher.get_data('users:' + user_id)
        if device_id is not None and device_id:
            user = UserType( decoded_data=user_data[0], key=user_id )
            if action == 'add':
                user.add_device(device_id=device_id)
            elif action == 'delete':
                user.delete_device(device_id=device_id)
            data = user.return_data()
            return self.s.Cacher.set_data('users:' + user_id, data)
        else:
            return False