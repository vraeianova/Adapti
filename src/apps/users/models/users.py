from django.contrib import admin
from django.contrib.auth.models import AbstractUser, Group, Permission

# Django
from django.db import models

from ..managers import CustomUserManager


class CustomUser(
    AbstractUser,
):
    """User model.
    Extend from Django's Abstract User, change the username field
    to email and add some extra fields.
    """

    username = None
    first_name = models.CharField("first name", max_length=150, blank=True)
    last_name = models.CharField("last name", max_length=150, blank=True)

    email = models.EmailField(
        "email address",
        unique=True,
        error_messages={"unique": "A user with that email already exists."},
    )
    email_confirmed = models.BooleanField(
        "verified",
        default=False,
        help_text="Set to true when the user have verified its email address.",
    )
    new_pass_confirmed = models.BooleanField(
        "NewPassConfirmed",
        default=True,
        help_text="Set to true when the user have verified its new pass.",
    )
    creation_date = models.DateField(
        db_column="CreationDate", blank=True, null=True
    )
    membership_date = models.DateField(
        db_column="MembershipDate", blank=True, null=True
    )

    groups = models.ManyToManyField(
        Group,
        related_name="customuser_set",  # Cambia 'user_set' a 'customuser_set'
        blank=True,
        help_text="The groups this user belongs to. A user will get all permissions granted to each of their groups.",
        related_query_name="customuser",
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name="customuser_permissions_set",  # Cambia 'user_permissions_set' a 'customuser_permissions_set'
        blank=True,
        help_text="Specific permissions for this user.",
        related_query_name="customuser",
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    objects = CustomUserManager()

    def __str__(self):
        """Return username."""
        return self.email


admin.site.register(CustomUser)
