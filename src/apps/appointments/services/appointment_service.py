from rest_framework import status

from apps.api.serializers.appointments_serializers import (
    AppointmentCreateSerializer,
    AppointmentSerializer,
)


class AppointmentService:
    @staticmethod
    def create_appointment(appointment_data: dict) -> dict:
        """
        Centraliza la lógica para crear una cita.
        Args:
            appointment_data (dict): Los datos de la cita.

        Returns:
            dict: Los datos de la cita creada o los errores de validación.
        """
        # Usar el serializador para validar y guardar la cita
        create_serializer = AppointmentCreateSerializer(data=appointment_data)

        if not create_serializer.is_valid():
            # Si los datos no son válidos, devolver los errores en el mismo formato que la vista original
            return {
                "error": "Failed to create appointment",
                "details": create_serializer.errors,
                "status_code": status.HTTP_400_BAD_REQUEST,
            }

        try:
            # Intentar guardar la cita
            appointment = create_serializer.save()
        except Exception as e:
            # Si hay algún error, devolver la misma estructura de error que en la vista
            return {
                "error": f"Failed to create appointment: {str(e)}",
                "status_code": status.HTTP_400_BAD_REQUEST,
            }

        # Si se crea correctamente, devolver los datos de la cita
        response_serializer = AppointmentSerializer(appointment)
        return {
            "data": response_serializer.data,
            "status_code": status.HTTP_201_CREATED,
        }
