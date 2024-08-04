import os

import requests
from dotenv import load_dotenv


load_dotenv()


class ZohoBookingsService:
    def __init__(self):
        self.account_url = os.getenv("ACCOUNT_URL")
        self.api_url = os.getenv("API_URL")
        self.client_id = os.getenv("CLIENT_ID")
        self.client_secret = os.getenv("CLIENT_SECRET")
        self.redirect_uri = os.getenv("REDIRECT_URI")
        self.authorization_code = os.getenv("AUTHORIZATION_CODE")
        self.access_token = (
            self.get_access_token()
        )  # Obtener el token de acceso al inicializar

    def get_access_token(self):
        url = f"{self.account_url}/oauth/v2/token"
        payload = {
            "grant_type": "authorization_code",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "redirect_uri": self.redirect_uri,
            "code": self.authorization_code,
        }
        response = requests.post(url, data=payload)
        response_data = response.json()
        if "access_token" in response_data:
            self.access_token = response_data["access_token"]
        else:
            raise Exception("Failed to obtain access token.")
        return self.access_token

    def get_headers(self):
        if not self.access_token:
            self.access_token = (
                self.get_access_token()
            )  # Reintentar obtener el token si no está disponible
        return {
            "Authorization": f"Zoho-oauthtoken {self.access_token}",
            "Content-Type": "application/json",
        }

    def get_workspaces(self, workspace_id=None):
        url = f"{self.api_url}/workspaces"
        if workspace_id:
            url += f"?workspace_id={workspace_id}"
        headers = self.get_headers()
        response = requests.get(url, headers=headers)
        return response.json()
