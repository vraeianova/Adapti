from rest_framework import serializers

from apps.appointments.models import Appointment


class AppointmentSerializer(serializers.ModelSerializer):
    # appointment_status = AppointmentStatusSerializer()
    # doctor = DoctorSerializer()
    # patient = PatientSerializer()

    class Meta:
        model = Appointment
        fields = [
            "id",
            # "doctor",
            "appointment_date",
            "start_time",
            "end_time",
            # "appointment_status",
            # "patient",
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
