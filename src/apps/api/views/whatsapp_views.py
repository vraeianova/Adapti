import asyncio

from bot.services.bot_service import BotService
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView


processed_messages = set()


class WhatsappWebhook(APIView):
    permission_classes = [AllowAny]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bot_service = BotService()

    def post(self, request, *args, **kwargs):
        try:
            incoming_msg = request.data.get("Body", "")
            from_number = request.data.get("From", "")
            message_sid = request.data.get("MessageSid", "")

            if not incoming_msg or not from_number or not message_sid:
                return Response(status=400)

            if message_sid in processed_messages:
                print(f"Message with SID {message_sid} processed")
                return Response(status=200)

            processed_messages.add(message_sid)

            response_text = asyncio.run(
                self.bot_service.handle_message(incoming_msg, from_number)
            )

            return Response({"message": response_text}, status=200)
        except Exception as e:
            print(f"error: {str(e)}")
            return Response({"error": str(e)}, status=500)
