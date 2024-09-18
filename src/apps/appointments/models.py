from django.contrib import admin
from django.core.exceptions import ValidationError
from django.db import models

from apps.doctors.models import Doctor


class AppointmentType(models.Model):
    id = models.AutoField(db_column="IdAppointmentType", primary_key=True)
    description = models.CharField(db_column="Description", max_length=350)

    class Meta:
        db_table = "AppointmentType"

    def __str__(self):
        return self.description


class AppointmentStatus(models.Model):
    id = models.AutoField(db_column="IdAppointmentStatus", primary_key=True)
    description = models.CharField(db_column="Description", max_length=350)

    class Meta:
        db_table = "AppointmentStatus"

    def __str__(self):
        return self.description


class Appointment(models.Model):
    id = models.AutoField(db_column="IdAppointment", primary_key=True)
    doctor = models.ForeignKey(
        Doctor, models.DO_NOTHING, db_column="Doctor", blank=False, null=False
    )
    appointment_date = models.DateField(
        db_column="AppointmentDate", blank=False, null=False
    )
    start_time = models.TimeField(
        db_column="StartTime", blank=False, null=False
    )
    end_time = models.TimeField(db_column="EndTime", blank=False, null=False)
    appointment_status = models.ForeignKey(
        AppointmentStatus,
        models.DO_NOTHING,
        db_column="AppointmentStatus",
        blank=True,
        null=True,
    )
    # patient = models.ForeignKey(
    #     Patient,
    #     models.DO_NOTHING,
    #     db_column="Patient",
    #     blank=False,
    #     null=False,
    # )
    creation_date = models.DateTimeField(
        db_column="CreationDate", auto_now_add=True
    )
    appointment_type = models.CharField(
        db_column="AppointmentType", max_length=100, blank=True, null=True
    )
    notes = models.TextField(db_column="Notes", blank=True, null=True)

    class Meta:
        db_table = "Appointment"
        unique_together = ("doctor", "appointment_date", "start_time")

    def __str__(self):
        return f"Cita con {self.doctor} el {self.appointment_date} a las {self.start_time}"

    def clean(self):
        # Validación para evitar conflictos en las citas del doctor
        overlapping_appointments = Appointment.objects.filter(
            doctor=self.doctor,
            appointment_date=self.appointment_date,
            start_time__lt=self.end_time,
            end_time__gt=self.start_time,
        ).exclude(pk=self.pk)

        if overlapping_appointments.exists():
            raise ValidationError(
                "El doctor ya tiene una cita en este horario."
            )

        # Validación para evitar que el paciente tenga dos citas al mismo tiempo
        overlapping_patient_appointments = Appointment.objects.filter(
            patient=self.patient,
            appointment_date=self.appointment_date,
            start_time__lt=self.end_time,
            end_time__gt=self.start_time,
        ).exclude(pk=self.pk)

        if overlapping_patient_appointments.exists():
            raise ValidationError(
                "El paciente ya tiene una cita en este horario."
            )


admin.site.register(Appointment)
admin.site.register(AppointmentStatus)
