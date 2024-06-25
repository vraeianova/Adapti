import asyncio
import os

from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from dotenv import load_dotenv
from twilio.rest import Client

from apps.bot.services.bot_service import BotService


load_dotenv()

processed_messages = set()


@method_decorator(csrf_exempt, name="dispatch")
class WhatsAppService(View):
    def __init__(self):
        self.TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
        self.TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
        self.TWILIO_WHATSAPP_NUMBER_SANDBOX = os.getenv(
            "TWILIO_WHATSAPP_NUMBER_SANDBOX"
        )
        self.client = Client(self.TWILIO_ACCOUNT_SID, self.TWILIO_AUTH_TOKEN)
        self.bot_service = BotService()

    def post(self, request, *args, **kwargs):

        try:
            incoming_msg = request.POST.get("Body", "")
            from_number = request.POST.get("From", "")
            message_sid = request.POST.get("MessageSid", "")

            if not incoming_msg or not from_number or not message_sid:
                return HttpResponse(status=400)

            if message_sid in processed_messages:
                print(f"Message with SID {message_sid} processed")
                return HttpResponse(status=200)

            processed_messages.add(message_sid)

            response_text = asyncio.run(
                self.bot_service.handle_message(incoming_msg)
            )
            self.send_message(from_number, response_text)

            return HttpResponse(status=200)
        except Exception as e:
            return HttpResponse(str(e), status=500)

    def send_message(self, to_number, message_body):
        try:
            message = self.client.messages.create(
                body=message_body,
                from_=self.TWILIO_WHATSAPP_NUMBER_SANDBOX,
                to=to_number,
            )
            print(f"Message sent with SID: {message.sid}")
        except Exception as e:
            print(f"An error has ocurred: {str(e)}")
