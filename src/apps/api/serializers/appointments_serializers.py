from django.utils import timezone
from rest_framework import serializers

from apps.api.serializers.doctor_serializers import DoctorSerializer
from apps.api.serializers.patient_serializers import PatientSerializer
from apps.appointments.models import Appointment, AppointmentStatus


class AppointmentStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppointmentStatus
        fields = ["id", "description"]


class AppointmentSerializer(serializers.ModelSerializer):
    doctor = DoctorSerializer()
    appointment_status = AppointmentStatusSerializer()
    patient = PatientSerializer()
    # doctor = serializers.PrimaryKeyRelatedField(queryset=Doctor.objects.all())

    class Meta:
        model = Appointment
        fields = [
            "id",
            "doctor",
            "appointment_date",
            "start_time",
            "end_time",
            "appointment_status",
            "patient",
            "creation_date",
            "appointment_type",
            "notes",
        ]


class AppointmentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = [
            "doctor",
            "appointment_date",
            "start_time",
            "end_time",
            "appointment_status",
            "patient",
            "appointment_type",
            "notes",
        ]

    def validate(self, data):
        appointment_date = data.get("appointment_date")
        start_time = data.get("start_time")
        end_time = data.get("end_time")
        doctor = data.get("doctor")
        patient = data.get("patient")

        # Validación para evitar conflictos en las citas del doctor
        overlapping_appointments = Appointment.objects.filter(
            doctor=doctor,
            appointment_date=appointment_date,
            start_time__lt=end_time,
            end_time__gt=start_time,
        )

        if self.instance:
            overlapping_appointments = overlapping_appointments.exclude(
                pk=self.instance.pk
            )

        if overlapping_appointments.exists():
            raise serializers.ValidationError(
                "The doctor already has an appointment at this time."
            )

        # Validación para evitar que el paciente tenga dos citas al mismo tiempo
        overlapping_patient_appointments = Appointment.objects.filter(
            patient=patient,
            appointment_date=appointment_date,
            start_time__lt=end_time,
            end_time__gt=start_time,
        )

        if self.instance:
            overlapping_patient_appointments = (
                overlapping_patient_appointments.exclude(pk=self.instance.pk)
            )

        if overlapping_patient_appointments.exists():
            raise serializers.ValidationError(
                "The patient already has an appointment at this time."
            )

        return data

    def validate_appointment_date(self, value):
        if value < timezone.now().today().date():
            raise serializers.ValidationError(
                "No se puede crear una cita en el pasado."
            )
        return value
