from rest_framework import serializers

from apps.doctors.models import Doctor, DoctorStatus


class DoctorStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = DoctorStatus
        fields = ["id", "description"]


class DoctorSerializer(serializers.ModelSerializer):
    doctor_status = DoctorStatusSerializer()

    class Meta:
        model = Doctor
        fields = [
            "id",
            "first_name",
            "last_name",
            "description",
            "profile_pic",
            "doctor_status",
            "specialization",
            "contact_email",
            "contact_phone",
        ]
