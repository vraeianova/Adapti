import os

from twilio.rest import Client


class WhatsappService:
    def __init__(self):
        self.account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        self.auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        # self.whatsapp_number = os.getenv("TWILIO_WHATSAPP_NUMBER_SANDBOX")
        self.client = Client(self.account_sid, self.auth_token)

    def send_whatsapp_message(self, to_number, message_body, from_number):
        try:
            message = self.client.messages.create(
                body=message_body,
                from_=from_number,
                to=to_number,
            )
            print(f"Message sent with SID: {message.sid}")
            return message.sid
        except Exception as e:
            print(f"An error has occurred: {str(e)}")
            raise e
