import json
import singleton


class Shares:

    def __init__(self):
        self.s = singleton.Singleton()

    def handle_group_share(self, data, group_id, owner_id, key):
        key_parsed = json.loads(key)
        data_list = json.loads(data)
        shares = {'headers': [], 'items': []}
        group_id_parsed = json.loads(group_id).replace('"', '')
        owner_parsed = json.loads(owner_id).replace('"', '')
        shares_ref = self.s.Firebase.db.collection('groups').document(group_id_parsed).collection('shares')
        for header in data_list['headers']:
            header['shareType'] = key_parsed['headers']
            header['groupId'] = group_id_parsed
            doc_ref = shares_ref.document(header['id'])
            doc_snapshot = doc_ref.get()
            if not doc_snapshot.exists:
                doc_ref.set(header, merge=True)
                shares['headers'].append(header['id'])
        for item in data_list['items']:
            item['shareType'] = key_parsed['items']
            item['groupId'] = group_id_parsed
            doc_ref = shares_ref.document(item['id'])
            doc_snapshot = doc_ref.get()
            if not doc_snapshot.exists:
                doc_ref.set(item, merge=True)
                shares['items'].append(item['id'])
        data = self.s.Messages.get_most_recent_message(group_id_parsed)
        message, message_id = data['message'], data['message_id']
        message_type = None
        message_owner = None
        if message is not None:
            message_type = message['type'].replace('"', '')
            message_owner = message['owner'].replace('"', '')
        if message is None or message_type != 'SHARE' or message_owner != owner_parsed:
            self.s.Messages.create_message(group_id_parsed, owner_id, shares, key_parsed, 'SHARE')
        else:
            self.s.Messages.create_message(group_id_parsed, owner_id, shares, key_parsed, 'SHARE', message_id)
        return 'success'
