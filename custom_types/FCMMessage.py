import os
import requests
import json

from aiofiles.os import access
from google.oauth2 import service_account
import google.auth.transport.requests
import singleton

class FCMMessage:
    title = ''
    body = ''
    data: dict = {}

    def __init__(self, token: str):
        self.s = singleton.Singleton()
        self.token = token
        self.url = "https://fcm.googleapis.com/v1/projects/sommme-8f45f/messages:send"
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # Adjust as needed
        self.service_account_path = os.path.join(
            project_root, "private/serviceAccountKey.json"
        )
        self.credentials = service_account.Credentials.from_service_account_file(
            self.service_account_path,
            scopes=["https://www.googleapis.com/auth/firebase.messaging"]
        )


    def set_notification(self, title, body):
        self.title = title
        self.body = body

    def get_access_token(self) -> str:
        """
        Generate an access token from the service account credentials.

        :return: OAuth2 access token.
        """
        request = google.auth.transport.requests.Request()
        self.credentials.refresh(request)
        return self.credentials.token

    def set_data(self, data):
        self.data = data

    def send_message(self):
        """
        Send a message using FCM.

        :param token: The recipient device token.
        :param title: The notification title.
        :param body: The notification body.
        :param data: A dictionary of custom data.
        :return: Response from the FCM API.
        """

        retrieved_token = self.s.Cacher.get_data('fcm_token')
        if not retrieved_token:
            access_token = self.get_access_token()
            self.s.Cacher.set_data('fcm_token', access_token, '', '', 3550)
        else:
            access_token = retrieved_token[0]
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }

        payload = {
            "message": {
                "token": self.token,
                "android": {
                    "priority": "high",
                    "notification": {
                        "title": self.title,
                        "body": self.body,
                        "sound": "default",
                    },
                },
                "apns": {
                    "headers": {
                        "apns-priority": "10",
                    },
                    "payload": {
                        "aps": {
                            "alert": {
                                "title": self.title,
                                "body": self.body,
                            },
                            "sound": "default",
                            "badge": 1,  # Optional: Update app icon badge
                        }
                    },
                },
                "data": self.data
            }
        }

        response = requests.post(self.url, headers=headers, data=json.dumps(payload))
        return response.json()