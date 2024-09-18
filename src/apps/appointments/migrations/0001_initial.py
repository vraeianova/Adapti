# Generated by Django 4.2 on 2024-09-18 20:58

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("doctors", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="AppointmentStatus",
            fields=[
                (
                    "id",
                    models.AutoField(
                        db_column="IdAppointmentStatus",
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                (
                    "description",
                    models.CharField(db_column="Description", max_length=350),
                ),
            ],
            options={
                "db_table": "AppointmentStatus",
            },
        ),
        migrations.CreateModel(
            name="Appointment",
            fields=[
                (
                    "id",
                    models.AutoField(
                        db_column="IdAppointment",
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                (
                    "appointment_date",
                    models.DateField(db_column="AppointmentDate"),
                ),
                ("start_time", models.TimeField(db_column="StartTime")),
                ("end_time", models.TimeField(db_column="EndTime")),
                (
                    "creation_date",
                    models.DateTimeField(
                        auto_now_add=True, db_column="CreationDate"
                    ),
                ),
                (
                    "appointment_type",
                    models.CharField(
                        blank=True,
                        db_column="AppointmentType",
                        max_length=100,
                        null=True,
                    ),
                ),
                (
                    "notes",
                    models.TextField(blank=True, db_column="Notes", null=True),
                ),
                (
                    "appointment_status",
                    models.ForeignKey(
                        blank=True,
                        db_column="AppointmentStatus",
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        to="appointments.appointmentstatus",
                    ),
                ),
                (
                    "doctor",
                    models.ForeignKey(
                        db_column="Doctor",
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        to="doctors.doctor",
                    ),
                ),
            ],
            options={
                "db_table": "Appointment",
                "unique_together": {
                    ("doctor", "appointment_date", "start_time")
                },
            },
        ),
    ]
