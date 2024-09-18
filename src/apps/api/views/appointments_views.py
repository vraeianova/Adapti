from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.api.serializers.appointments_serializers import (  # DoctorSerializer,; PatientSerializer,
    AppointmentCreateSerializer,
    AppointmentSerializer,
)
from apps.appointments.models import Appointment


# from apps.doctors.models import Doctor
# from apps.patients.models import Patient


class AppointmentCreateView(APIView):
    def post(self, request, *args, **kwargs):
        create_serializer = AppointmentCreateSerializer(data=request.data)
        if not create_serializer.is_valid():
            return Response(
                create_serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            appointment = create_serializer.save()
        except Exception as e:
            return Response(
                {"error": f"Failed to create appointment: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        response_serializer = AppointmentSerializer(appointment)
        return Response(
            response_serializer.data, status=status.HTTP_201_CREATED
        )


class AppointmentViewSet(viewsets.ModelViewSet):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return AppointmentCreateSerializer
        return AppointmentSerializer

    def perform_create(self, serializer):
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()
