from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.api.serializers.assistants_serializers import (
    AssistantCreateSerializer,
    AssistantSerializer,
)
from apps.openai.config import OpenAIConfig


class AssistantCreateView(APIView):
    def post(self, request, *args, **kwargs):
        # Validar los datos de entrada utilizando el serializador específico para creación
        create_serializer = AssistantCreateSerializer(data=request.data)
        if not create_serializer.is_valid():
            return Response(
                create_serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )

        openai_config = OpenAIConfig()
        assistant_service = openai_config.get_assistant_service()

        try:
            openai_assistant = assistant_service.create_assistant(
                model=create_serializer.validated_data["model"],
                name=create_serializer.validated_data["name"],
                instructions=create_serializer.validated_data["instructions"],
                tools=create_serializer.validated_data["tools"],
                response_format=request.data.get("response_format", "auto"),
                temperature=request.data.get("temperature", 1.0),
                top_p=request.data.get("top_p", 1.0),
                tool_resources=create_serializer.validated_data.get(
                    "tool_resources", {}
                ),
            )
        except Exception as e:
            return Response(
                {"error": f"Failed to create assistant: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not openai_assistant or not hasattr(openai_assistant, "id"):
            return Response(
                {"error": "Failed to create assistant with OpenAI."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        openai_assistant_dict = openai_assistant.to_dict()
        assistant_data = {
            "assistant_id": openai_assistant_dict["id"],
            "name": openai_assistant_dict["name"],
            "description": openai_assistant_dict.get("description", ""),
            "instructions": openai_assistant_dict["instructions"],
            "model": openai_assistant_dict["model"],
            "temperature": openai_assistant_dict["temperature"],
            "top_p": openai_assistant_dict["top_p"],
            "response_format": openai_assistant_dict["response_format"],
            "tools": openai_assistant_dict["tools"],
            "tool_resources": openai_assistant_dict["tool_resources"],
        }

        db_serializer = AssistantSerializer(data=assistant_data)
        if db_serializer.is_valid():
            db_serializer.save()
            return Response(db_serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(
                db_serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )
