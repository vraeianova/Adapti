from datetime import timedelta

import requests
from django.utils import timezone

from apps.oauthtoken.models import OauthToken


class ZohoAuth:
    def __init__(
        self,
        client_id,
        client_secret,
        redirect_uri,
        account_url,
        authorization_code=None,
    ):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.account_url = account_url
        self.authorization_code = authorization_code
        self.access_token = None
        self.refresh_token = None
        self.token_expiry = None
        self.load_tokens()

    def save_tokens(self, access_token, refresh_token, expires_in):
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.token_expiry = timezone.now() + timedelta(seconds=expires_in)
        print(
            f"Attempting to save tokens: Access Token - {access_token}, Refresh Token - {refresh_token}, Expiry - {self.token_expiry}"
        )
        try:
            OauthToken.objects.filter(provider="zoho").delete()
            token = OauthToken(
                provider="zoho",
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
            token = OauthToken.objects.filter(provider="zoho").first()
            if token:
                self.access_token = token.access_token
                self.refresh_token = token.refresh_token
                self.token_expiry = token.token_expiry
                print("Access token loaded ", self.access_token)
                print("Refresh token loaded", self.access_token)
            else:
                print(
                    "No existing tokens found. Authorization Code is required to obtain new tokens."
                )
                if self.authorization_code:
                    self.get_token()
                else:
                    raise Exception(
                        "Authorization code is required to obtain new tokens."
                    )
        except Exception as e:
            print(f"Failed to load tokens: {e}")

    def get_token(self):
        url = f"{self.account_url}/oauth/v2/token"
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "redirect_uri": self.redirect_uri,
            "grant_type": "authorization_code",
            "code": self.authorization_code,  # Using the injected Authorization Code
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
