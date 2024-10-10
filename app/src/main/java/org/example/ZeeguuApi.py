import requests
import json

class ZeeguuApi:
    def __init__(self, base_url, email, password):
        self.base_url = base_url
        self.email = email
        self.password = password
        self.session = self.get_user_session()

    def get_user_session(self):
        try:
            url = f"{self.base_url}/session/{self.email}"
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
                'Accept': 'application/json'
            }
            data = {
                'password': self.password
            }
            response = requests.post(url, data=data, headers=headers)
            response.raise_for_status()
            return response.json().get('session')
        except Exception as e:
            print(f"An error occurred: {e}")
            return None

    def send_http_request(self, endpoint, body):
        try:
            url = f"{self.base_url}{endpoint}?session={self.session}"
            headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
            response = requests.post(url, json=body, headers=headers)
            response.raise_for_status()
            return response.elapsed.microseconds
        except Exception as e:
            print(f"An error occurred: {e}")
            return None