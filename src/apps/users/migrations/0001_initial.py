# Generated by Django 4.2 on 2024-08-31 19:28

import apps.utils.directory_path
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
    ]

    operations = [
        migrations.CreateModel(
            name="CustomUser",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "password",
                    models.CharField(max_length=128, verbose_name="password"),
                ),
                (
                    "last_login",
                    models.DateTimeField(
                        blank=True, null=True, verbose_name="last login"
                    ),
                ),
                (
                    "is_superuser",
                    models.BooleanField(
                        default=False,
                        help_text="Designates that this user has all permissions without explicitly assigning them.",
                        verbose_name="superuser status",
                    ),
                ),
                (
                    "is_staff",
                    models.BooleanField(
                        default=False,
                        help_text="Designates whether the user can log into this admin site.",
                        verbose_name="staff status",
                    ),
                ),
                (
                    "is_active",
                    models.BooleanField(
                        default=True,
                        help_text="Designates whether this user should be treated as active. Unselect this instead of deleting accounts.",
                        verbose_name="active",
                    ),
                ),
                (
                    "date_joined",
                    models.DateTimeField(
                        default=django.utils.timezone.now,
                        verbose_name="date joined",
                    ),
                ),
                (
                    "first_name",
                    models.CharField(
                        blank=True, max_length=150, verbose_name="first name"
                    ),
                ),
                (
                    "last_name",
                    models.CharField(
                        blank=True, max_length=150, verbose_name="last name"
                    ),
                ),
                (
                    "email",
                    models.EmailField(
                        error_messages={
                            "unique": "A user with that email already exists."
                        },
                        max_length=254,
                        unique=True,
                        verbose_name="email address",
                    ),
                ),
                (
                    "email_confirmed",
                    models.BooleanField(
                        default=False,
                        help_text="Set to true when the user have verified its email address.",
                        verbose_name="verified",
                    ),
                ),
                (
                    "new_pass_confirmed",
                    models.BooleanField(
                        default=True,
                        help_text="Set to true when the user have verified its new pass.",
                        verbose_name="NewPassConfirmed",
                    ),
                ),
                (
                    "creation_date",
                    models.DateField(
                        blank=True, db_column="CreationDate", null=True
                    ),
                ),
                (
                    "membership_date",
                    models.DateField(
                        blank=True, db_column="MembershipDate", null=True
                    ),
                ),
                (
                    "groups",
                    models.ManyToManyField(
                        blank=True,
                        help_text="The groups this user belongs to. A user will get all permissions granted to each of their groups.",
                        related_name="customuser_set",
                        related_query_name="customuser",
                        to="auth.group",
                    ),
                ),
                (
                    "user_permissions",
                    models.ManyToManyField(
                        blank=True,
                        help_text="Specific permissions for this user.",
                        related_name="customuser_permissions_set",
                        related_query_name="customuser",
                        to="auth.permission",
                    ),
                ),
            ],
            options={
                "verbose_name": "user",
                "verbose_name_plural": "users",
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="Profile",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "address",
                    models.TextField(
                        blank=True, db_column="Address", null=True
                    ),
                ),
                (
                    "phone",
                    models.CharField(
                        blank=True, db_column="Phone", max_length=20, null=True
                    ),
                ),
                (
                    "photo",
                    models.ImageField(
                        blank=True,
                        db_column="Photo",
                        null=True,
                        upload_to=apps.utils.directory_path.user_profile_pic_directory_path,
                        verbose_name="profile picture",
                    ),
                ),
                (
                    "birth_date",
                    models.DateField(
                        blank=True, db_column="BirthDate", null=True
                    ),
                ),
                (
                    "gender",
                    models.IntegerField(
                        choices=[(1, "Masculino"), (2, "Femenino")]
                    ),
                ),
                (
                    "id_user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]
