from rest_framework import serializers

from apps.openai.models import Assistant


class AssistantCreateSerializer(serializers.Serializer):
    model = serializers.CharField(max_length=100)
    name = serializers.CharField(max_length=255)
    instructions = serializers.CharField()
    tools = serializers.JSONField(default=list)
    tool_resources = serializers.JSONField(default=dict, required=False)


class AssistantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assistant
        fields = "__all__"
