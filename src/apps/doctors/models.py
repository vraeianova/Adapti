from django.contrib import admin
from django.db import models

from apps.utils.directory_path import user_profile_pic_directory_path


class DoctorStatus(models.Model):
    id = models.AutoField(db_column="IdDoctorStatus", primary_key=True)
    description = models.CharField(db_column="Description", max_length=350)

    class Meta:
        db_table = "DoctorStatus"

    def __str__(self):
        return self.description


class Doctor(models.Model):
    id = models.AutoField(db_column="IdDoctor", primary_key=True)
    first_name = models.CharField(db_column="FirstName", max_length=30)
    last_name = models.CharField(db_column="LastName", max_length=30)
    slug = models.SlugField(
        db_column="Slug", max_length=50
    )  # TODO DELETE THIS
    description = models.TextField(
        db_column="Description", blank=True, null=True
    )
    profile_pic = models.ImageField(
        "ProfilePic",
        db_column="Photo",
        upload_to=user_profile_pic_directory_path,
        blank=True,
        null=True,
    )
    doctor_status = models.ForeignKey(
        DoctorStatus,
        models.DO_NOTHING,
        db_column="DoctorStatus",
        blank=True,
        null=True,
    )
    specialization = models.CharField(
        db_column="Specialization", max_length=100, blank=True, null=True
    )
    contact_email = models.EmailField(
        db_column="ContactEmail", blank=True, null=True
    )
    contact_phone = models.CharField(
        db_column="ContactPhone", max_length=15, blank=True, null=True
    )
    is_deleted = models.BooleanField(db_column="IsDeleted", default=False)

    class Meta:
        db_table = "Doctor"

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class DoctorAvailability(models.Model):
    DAY_OF_WEEK_CHOICES = [
        (0, "Lunes"),
        (1, "Martes"),
        (2, "Miércoles"),
        (3, "Jueves"),
        (4, "Viernes"),
        (5, "Sábado"),
        (6, "Domingo"),
    ]

    id = models.AutoField(db_column="IdDoctorAvailability", primary_key=True)
    doctor = models.ForeignKey(
        Doctor, models.DO_NOTHING, db_column="Doctor", blank=False, null=False
    )
    day_of_week = models.IntegerField(
        choices=DAY_OF_WEEK_CHOICES, db_column="DayOfWeek"
    )
    start_time = models.TimeField(
        db_column="StartTime", blank=False, null=False
    )
    end_time = models.TimeField(db_column="EndTime", blank=False, null=False)
    is_active = models.BooleanField(db_column="IsActive", default=True)

    class Meta:
        db_table = "DoctorAvailability"

    def __str__(self):
        return f"{self.get_day_of_week_display()} {self.start_time} - {self.end_time}"


class DoctorUnavailableDate(models.Model):
    id = models.AutoField(
        db_column="IdDoctorUnavailableDate", primary_key=True
    )
    doctor = models.ForeignKey(
        Doctor, models.DO_NOTHING, db_column="Doctor", blank=False, null=False
    )
    date = models.DateField(db_column="Date", blank=False, null=False)
    reason = models.CharField(
        db_column="Reason", max_length=255, blank=True, null=True
    )

    class Meta:
        db_table = "DoctorUnavailableDate"

    def __str__(self):
        return (
            f"{self.doctor} no está disponible el {self.date} ({self.reason})"
        )


admin.site.register(DoctorStatus)
admin.site.register(Doctor)
admin.site.register(DoctorAvailability)
admin.site.register(DoctorUnavailableDate)
