from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.api.serializers.conversations_serializers import ThreadSerializer
from apps.conversations.models import Thread


class HumanInterventionUpdateView(APIView):
    def get_object(self, thread_id):
        try:
            return Thread.objects.get(thread_id=thread_id)
        except Thread.DoesNotExist:
            return None

    def patch(self, request, thread_id, *args, **kwargs):
        """
        Update the human_intervention_needed flag and other fields of the thread.

        Args:
            thread_id (str): The ID of the thread to update.

        Returns:
            Response: JSON response with the updated thread or an error message.
        """
        thread = self.get_object(thread_id)
        if not thread:
            return Response(
                {"error": "Thread not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Deserialize the request data
        serializer = ThreadSerializer(
            thread, data=request.data, partial=True
        )  # `partial=True` allows partial updates
        if serializer.is_valid():
            serializer.save()  # Save the changes to the Thread model
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )
