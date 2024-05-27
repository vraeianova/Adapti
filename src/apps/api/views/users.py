from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.api.serializers.users import SignUpSerializer
from apps.users.models import Profile

from ..serializers import CustomerSerializer


User = get_user_model()


class CustomerProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        try:

            profile = user.profile
            serializer = CustomerSerializer(profile)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Profile.DoesNotExist:
            return Response(
                {"error": "Profile not found."},
                status=status.HTTP_404_NOT_FOUND,
            )


class SignupView(CreateAPIView):
    serializer_class = SignUpSerializer
