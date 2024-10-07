from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.bot.services.bot_service import BotService


processed_messages = set()


class WhatsappWebhook(APIView):
    permission_classes = [AllowAny]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bot_service = BotService("whatsapp")

    def post(self, request, *args, **kwargs):
        # Obtener el cuerpo del mensaje, números de origen y destino, y el SID del mensaje
        incoming_msg = request.data.get("Body", "")
        from_number = request.data.get("From", "")
        to_number = request.data.get("To", "")
        message_sid = request.data.get("MessageSid", "")
        profile_name = request.data.get("ProfileName", "")

        if (
            not incoming_msg
            or not from_number
            or not to_number
            or not message_sid
            or not profile_name
        ):
            return Response(
                {"error": "Missing necessary message details."}, status=400
            )

        if message_sid in processed_messages:
            return Response({"info": "Message already processed"}, status=200)

        processed_messages.add(message_sid)

        enriched_msg = f"{profile_name} says: {incoming_msg}."

        self.bot_service.handle_message(
            enriched_msg,
            {
                "from_number": from_number,
                "to_number": to_number,
            },
        )

        return Response({"status": "Message is being processed"}, status=200)
