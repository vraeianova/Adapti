import asyncio

from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.bot.services.bot_service import BotService


processed_messages = set()


class WhatsappWebhook(APIView):
    permission_classes = [AllowAny]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bot_service = BotService()

    def post(self, request, *args, **kwargs):
        # Extraer el cuerpo del mensaje y los números de interés desde la solicitud de Twilio
        incoming_msg = request.data.get(
            "Body", ""
        )  # Mensaje recibido del cliente externo
        from_number = request.data.get(
            "From", ""
        )  # Número de WhatsApp del cliente externo
        to_number = request.data.get(
            "To", ""
        )  # Número de WhatsApp de la clínica (negocio)
        message_sid = request.data.get(
            "MessageSid", ""
        )  # Identificador único del mensaje

        # Validar que toda la información necesaria esté presente
        if (
            not incoming_msg
            or not from_number
            or not to_number
            or not message_sid
        ):
            return Response(
                {"error": "Missing necessary message details."}, status=400
            )

        # Verificar si el mensaje ya fue procesado
        if message_sid in processed_messages:
            return Response({"info": "Message already processed"}, status=200)

        # Marcar el mensaje como procesado
        processed_messages.add(message_sid)

        # Ejecutar la lógica del bot para procesar el mensaje y responder

        self.bot_service.handle_message(
            incoming_msg,  # Contenido del mensaje
            "whatsapp",  # Canal utilizado
            {
                "from_number": from_number,
                "to_number": to_number,
            },  # Números involucrados
        )

        # Responder que el mensaje está siendo procesado
        return Response({"status": "Message is being processed"}, status=200)
