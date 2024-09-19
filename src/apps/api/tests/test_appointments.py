from datetime import datetime, timedelta

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.doctors.models import Doctor
from apps.patients.models import Patient


class TestAppointmentCreateView(APITestCase):

    def setUp(self):
        self.doctor = Doctor.objects.create(
            first_name="John",
            last_name="Doe",
            contact_email="john.doe@example.com",
        )
        self.patient = Patient.objects.create(
            name="Emily Smith",
            phone_number="+1234567890",
            address="123 Main St",
        )
        self.appointment_date = (datetime.today() + timedelta(days=1)).date()

    def test_create_appointment_conflict(self):
        url = reverse("appointment-create")

        # Crea la primera cita
        data_1 = {
            "doctor": self.doctor.id,
            "appointment_date": self.appointment_date,
            "start_time": "10:00",
            "end_time": "11:00",
            "patient": self.patient.id,
        }
        response_1 = self.client.post(url, data_1, format="json")
        self.assertEqual(response_1.status_code, status.HTTP_201_CREATED)

        # Intenta crear una segunda cita en el mismo horario
        data_2 = {
            "doctor": self.doctor.id,
            "appointment_date": self.appointment_date,
            "start_time": "10:00",  # Mismo horario
            "end_time": "11:00",
            "patient": self.patient.id,
        }
        response_2 = self.client.post(url, data_2, format="json")

        # Verifica que la segunda cita no pueda crearse debido a conflicto
        self.assertEqual(response_2.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("non_field_errors", response_2.data)

    def test_create_appointment_in_the_past(self):
        url = reverse("appointment-create")
        # Fecha de la cita en el pasado
        past_date = datetime.now().date() - timedelta(days=1)
        data = {
            "doctor": self.doctor.id,
            "appointment_date": past_date,
            "start_time": "10:00",
            "end_time": "11:00",
            "patient": self.patient.id,
        }
        response = self.client.post(url, data, format="json")

        # Verificar que la API devuelve un error (400) al intentar crear una cita en el pasado
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # Verificar que el mensaje de error menciona la fecha
        self.assertIn("appointment_date", response.data)

    def test_create_appointment_success(self):
        url = reverse("appointment-create")
        data = {
            "doctor": self.doctor.id,
            "appointment_date": "2024-09-20",
            "start_time": "10:00",
            "end_time": "11:00",
            "patient": self.patient.id,
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["doctor"]["id"], self.doctor.id)

    def test_create_appointment_invalid_data(self):
        url = reverse("appointment-create")
        data = {
            "doctor": 99999,  # ID de doctor no válido
            "appointment_date": "2024-09-20",
            "start_time": "10:00",
            "end_time": "11:00",
            "patient": self.patient.id,
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("doctor", response.data)
