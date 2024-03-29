import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()


class MessageHelper:
    @staticmethod
    def button_template(id: str, title: str) -> dict[str, any]:
        return {
            "type": "reply",
            "reply": {
                "id": id,
                "title": title
            }
        }

    @staticmethod
    def section_row_template(id: str, title: str, description: str) -> dict[str, str]:
        return {
            "id": f"{id}",
            "title": f"{title}",
            "description": f"{description}"
        }

    @staticmethod
    def section_template(section_title: str, rows: list) -> dict[str, any]:
        section = {
            "title": f"{section_title}",
            "rows": [
            ]
        }
        for r in rows:
            section["rows"].append(r)
        return section


class NewMessage:
    def __init__(self):
        self.headers: dict[str,str] = {'Content-Type': 'application/json', 'Authorization': f'Bearer {os.environ["token"]}'}
        self.url: str = f"https://graph.facebook.com/{os.environ['version']}/{os.environ['phone-number-id']}/messages"
        self.payload: str = ""

    def configure_list_request(self, header: str, body: str, button_text: str, sections: list) -> None:
        self.payload = {
            "messaging_product": "whatsapp",
            "to": f"{os.environ['recipients-number']}",
            "type": "interactive",
            "interactive": {
                "type": "list",
                "header": {
                    "type": "text",
                    "text": f"{header}"
                },
                "body": {
                    "text": f"{body}"
                },
                "action": {
                    "button": f"{button_text}",
                    "sections": [
                    ]
                }
            }
        }
        for s in sections:
            self.payload["interactive"]["action"]["sections"].append(s)
        self.payload = json.dumps(self.payload)

    def configure_button_request(self, body: str, header: str, buttons: list) -> None:
        self.payload = {
            "messaging_product": "whatsapp",
            "to": f"{os.environ['recipients-number']}",
            "type": "interactive",
            "interactive": {
                "type": "button",
                "header": {
                    "type": "text",
                    "text": header
                },
                "body": {
                    "text": body
                },
                "action": {
                    "buttons": [
                    ]
                }
            }
        }
        for b in buttons:
            self.payload["interactive"]["action"]["buttons"].append(b)
        self.payload = json.dumps(self.payload)

    def configure_text_request(self, body: str) -> None:
        self.payload = json.dumps({
            "messaging_product": "whatsapp",
            "to": os.environ['recipients-number'],
            "type": "text",
            "text": {
                "body": body
            }
        })

    def configure_template_request(self) -> None:
        self.payload = json.dumps({
            "messaging_product": "whatsapp",
            "to": os.environ['recipients-number'],
            "type": "template",
            "template": {
                "name": "hello_world",
                "language": {
                    "code": "en_US"
                }
            }
        })

    def send(self) -> None:
        response: requests.Response = requests.request("POST", self.url, headers=self.headers, data=self.payload)
        if "More than 24 hours have passed since the recipient last replied to the sender number" in str(
                response.content):
            msg: NewMessage = NewMessage()
            msg.configure_template_request()
            msg.send()
