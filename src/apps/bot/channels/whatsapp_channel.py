from apps.bot.channels.base_channel import BaseCommunicationChannel
from apps.whatsapp.services.whatsapp_service import WhatsappService


class WhatsAppChannel(BaseCommunicationChannel):
    def __init__(self):
        self.whatsapp_service = WhatsappService()

    def send_message(self, to_number, message_body):
        return self.whatsapp_service.send_whatsapp_message(
            to_number, message_body
        )

    def receive_message(self, request):
        incoming_msg = request.data.get("Body", "")
        from_number = request.data.get("From", "")
        return incoming_msg, from_number
