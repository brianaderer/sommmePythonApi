import json

import singleton


class Shares:

    def __init__(self):
        self.s = singleton.Singleton()

    def handle_group_share(self, data, group_id, owner_id, prev_shares, users):
        shares = {'flights': [], 'tastings': []}
        group_id_parsed = json.loads(group_id).replace('"', '')
        owner_parsed = json.loads(owner_id).replace('"', '')
        shares_ref = self.s.Firebase.db.collection('groups').document(group_id_parsed).collection('shares')
        data_list = json.loads(data)
        data_dict = {}
        for datum in data_list:
            data_dict[datum['id']] = datum

        prev_shares_list = json.loads(prev_shares)
        data_ids = [datum['id'] for datum in data_list]

        # Compute the difference between prev_shares and data_ids
        shares_not_in_data = list(set(prev_shares_list) - set(data_ids))

        for share_id in shares_not_in_data:
            # Query documents where the field 'id' matches share_id
            query = shares_ref.where('id', '==', share_id).stream()

            for doc in query:
                # Get the document reference and delete it
                shares_ref.document(doc.id).delete()

        ids_not_in_shares = list(set(data_ids) - set(prev_shares_list))

        for key in ids_not_in_shares:
            item = data_dict[key]
            item['shareType'] = item['type']
            item['groupId'] = group_id_parsed
            doc_ref = shares_ref.document(item['id'])
            doc_snapshot = doc_ref.get()
            if not doc_snapshot.exists:
                doc_ref.set({'id': item['id'], 'type': item['id']}, merge=True)
                if item['type'] == 'flight':
                    shares['flights'].append(item['id'])
                if item['type'] == 'tasting':
                    shares['tastings'].append(item['id'])
        data = self.s.Messages.get_most_recent_message(group_id_parsed)
        message, message_id = data['message'], data['message_id']
        message_type = None
        message_owner = None
        if message is not None:
            message_type = message['type'].replace('"', '')
            message_owner = message['owner'].replace('"', '')
        if message is None or message_type != 'SHARE' or message_owner != owner_parsed:
            self.s.Messages.create_message(group_id_parsed, owner_id, shares, users, 'SHARE')
        else:
            self.s.Messages.create_message(group_id_parsed, owner_id, shares, users, 'SHARE', message_id)
        return 'success'
