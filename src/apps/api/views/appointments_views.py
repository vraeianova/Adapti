from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.api.serializers.appointments_serializers import (
    AppointmentCreateSerializer,
    AppointmentSerializer,
)
from apps.appointments.models import Appointment
from apps.appointments.services.appointment_service import AppointmentService


# from apps.doctors.models import Doctor
# from apps.patients.models import Patient


class AppointmentCreateView(APIView):
    def post(self, request, *args, **kwargs):
        # Llamamos al servicio para crear la cita
        result = AppointmentService.create_appointment(request.data)

        # Devolvemos la respuesta según el status code del servicio
        if "error" not in result:
            return Response(result["data"], status=result["status_code"])
        else:
            return Response(result["details"], status=result["status_code"])


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
