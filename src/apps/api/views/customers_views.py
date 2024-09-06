from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.api.serializers.assistants_serializers import (
    AssistantCreateSerializer,
    AssistantSerializer,
)
from apps.openai.config import OpenAIConfig
from apps.openai.models import Assistant


class CustomerCreateView(APIView):
    def post(self, request, *args, **kwargs):
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


class AssistantSyncView(APIView):
    def post(self, request, *args, **kwargs):
        openai_config = OpenAIConfig()
        assistant_service = openai_config.get_assistant_service()

        all_assistants = assistant_service.list_assistants()
        all_assistants_dict = all_assistants.to_dict()

        db_assistant_ids = set(
            Assistant.objects.values_list("assistant_id", flat=True)
        )

        new_assistants = [
            assistant
            for assistant in all_assistants_dict["data"]
            if assistant["id"] not in db_assistant_ids
        ]

        assistants_to_create = []
        for assistant_data in new_assistants:
            assistants_to_create.append(
                Assistant(
                    assistant_id=assistant_data["id"],
                    name=assistant_data["name"],
                    description=assistant_data.get("description"),
                    instructions=assistant_data["instructions"],
                    model=assistant_data["model"],
                    temperature=assistant_data.get("temperature", 1.0),
                    top_p=assistant_data.get("top_p", 1.0),
                    response_format=assistant_data.get(
                        "response_format", "auto"
                    ),
                    tools=assistant_data.get("tools", []),
                    tool_resources=assistant_data.get("tool_resources", {}),
                )
            )

        if assistants_to_create:
            Assistant.objects.bulk_create(assistants_to_create)

        return Response(
            {
                "message": f"{len(assistants_to_create)} assistants synchronized."
            },
            status=status.HTTP_201_CREATED,
        )
