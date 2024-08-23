import os
from typing import Dict, Optional

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import Resource, build

from src.apps.bot.models import OauthToken


class GoogleCalendarClient:
    SCOPES: list[str] = ["https://www.googleapis.com/auth/calendar"]
    redirect_uri: str = "http://localhost:8000/api/v1/bot/oauth2callback/"

    def __init__(self, token_file: str = "token.json") -> None:
        self.creds: Optional[Credentials] = None
        self.token_file: str = token_file
        self.authenticate()

    def _get_client_secrets_dict(self) -> Dict[str, Dict[str, Optional[str]]]:
        return {
            "web": {
                "client_id": os.getenv("GOOGLE_CLIENT_ID"),
                "project_id": os.getenv("GOOGLE_PROJECT_ID"),
                "auth_uri": os.getenv("GOOGLE_AUTH_URI"),
                "token_uri": os.getenv("GOOGLE_TOKEN_URI"),
                "auth_provider_x509_cert_url": os.getenv(
                    "GOOGLE_AUTH_PROVIDER_X509_CERT_URL"
                ),
                "client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),
            }
        }

    def authenticate(self) -> None:
        self.load_saved_credentials()

        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self._refresh_access_token()
            else:
                self.start_auth_flow()
            self.save_credentials()

    def load_saved_credentials(self) -> None:
        try:
            token = OauthToken.objects.get(provider="google")
            self.creds = Credentials(
                token=token.access_token,
                refresh_token=token.refresh_token,
                token_uri=token.token_uri,
                client_id=token.client_id,
                client_secret=token.client_secret,
                scopes=token.scopes,
            )
        except OauthToken.DoesNotExist:
            self.creds = None

    def _refresh_access_token(self) -> None:
        if self.creds:
            self.creds.refresh(Request())
            self.save_credentials()  # Save the new credentials

    def start_auth_flow(self, redirect_uri: str = redirect_uri) -> None:
        flow: InstalledAppFlow = InstalledAppFlow.from_client_config(
            self._get_client_secrets_dict(), self.SCOPES
        )

        if redirect_uri:
            flow.redirect_uri = redirect_uri

        self.creds = flow.run_local_server(port=9000)

    def save_credentials(self) -> None:
        if self.creds:
            token, _ = OauthToken.objects.update_or_create(
                provider="google",
                defaults={
                    "access_token": self.creds.token,
                    "refresh_token": self.creds.refresh_token,
                    "token_expiry": self.creds.expiry,
                    "client_id": self.creds.client_id,
                    "client_secret": self.creds.client_secret,
                    "token_uri": self.creds.token_uri,
                    "scopes": self.creds.scopes,
                },
            )

    def get_service(self) -> Resource:
        return build("calendar", "v3", credentials=self.creds)
