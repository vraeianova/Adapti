import os
from datetime import timedelta

import requests
from django.utils import timezone

from apps.bot.models import ZohoToken


class ZohoAuth:
    def __init__(self):
        self.client_id = os.getenv("CLIENT_ID")
        self.client_secret = os.getenv("CLIENT_SECRET")
        self.redirect_uri = os.getenv("REDIRECT_URI")
        self.account_url = os.getenv("ACCOUNT_URL")
        self.access_token = None
        self.refresh_token = None
        self.token_expiry = None
        self.load_tokens()  # Cargar los tokens existentes o generarlos si no existen

    def save_tokens(self, access_token, refresh_token, expires_in):
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.token_expiry = timezone.now() + timedelta(seconds=expires_in)
        print(
            f"Attempting to save tokens: Access Token - {access_token}, Refresh Token - {refresh_token}, Expiry - {self.token_expiry}"
        )
        try:
            ZohoToken.objects.all().delete()  # Eliminar todos los tokens existentes
            token = ZohoToken(
                access_token=access_token,
                refresh_token=refresh_token,
                token_expiry=self.token_expiry,
            )
            token.save()
            print("Tokens saved successfully")
        except Exception as e:
            print(f"Failed to save tokens: {e}")

    def load_tokens(self):
        try:
            token = ZohoToken.objects.first()
            if token:
                self.access_token = token.access_token
                self.refresh_token = token.refresh_token
                self.token_expiry = token.token_expiry
                print("Tokens loaded successfully")
            else:
                print("No existing tokens found, generating new tokens.")
                self.get_token()
        except Exception as e:
            print(f"Failed to load tokens: {e}")

    def get_token(self):
        url = f"{self.account_url}/oauth/v2/token"
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "redirect_uri": self.redirect_uri,
            "grant_type": "authorization_code",
            "code": os.getenv("AUTHORIZATION_CODE"),
        }

        response = requests.post(url, data=data)
        if response.status_code == 200:
            tokens = response.json()
            self.save_tokens(
                tokens["access_token"],
                tokens["refresh_token"],
                tokens["expires_in"],
            )
        else:
            print(
                f"Failed to obtain access token: {response.status_code} - {response.text}"
            )
            raise Exception("Failed to obtain access token.")

    def refresh_access_token(self):
        url = f"{self.account_url}/oauth/v2/token"
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "refresh_token",
            "refresh_token": self.refresh_token,
        }

        response = requests.post(url, data=data)
        if response.status_code == 200:
            tokens = response.json()
            self.save_tokens(
                tokens["access_token"],
                self.refresh_token,
                tokens["expires_in"],
            )
        else:
            print(
                f"Failed to refresh access token: {response.status_code} - {response.text}"
            )
            raise Exception("Failed to refresh access token.")

    def ensure_valid_access_token(self):
        if timezone.now() >= self.token_expiry:
            self.refresh_access_token()

    def get_access_token(self):
        self.ensure_valid_access_token()
        return self.access_token
