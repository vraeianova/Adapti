from rest_framework import serializers

from apps.conversations.models import Thread


class ThreadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Thread
        fields = [
            "id",
            "human_intervention_needed",
            "last_interaction",
        ]
