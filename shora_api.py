import requests
import hmac
import json


class ShoraMessage:
    def __init__(self, where, title, description=''):
        self.where = str(where)
        self.title = str(title)
        self.description = str(description)

    def to_json(self):
        return json.dumps({
            'place': self.where,
            'title': self.title,
            'description': self.description
        })


class ShoraAPI:
    def __init__(self, shora_url, sign_secret=None):
        self.shora_base_url = shora_url
        if sign_secret:
            self.mac = hmac.new(sign_secret.encode('utf-8'))

    def send_message(self, shora_message):
        payload = shora_message.to_json()
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'ShoraBot/1.0 (http://shora.ce.sharif.edu/)',
        }
        if self.mac:
            mac = self.mac
            mac.update(payload.encode('utf-8'))
            headers.update({'X-Mac': str(mac.hexdigest())})
        url = self.shora_base_url

        try:
            response = requests.post(url=url, headers=headers, timeout=10, data=payload).json()
            return True, response['message']
        except requests.exceptions.ConnectTimeout:
            return False, 'Timeout'
        except Exception:
            pass

        return False, 'Unknown'
