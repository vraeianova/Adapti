import os

import requests
from dotenv import load_dotenv


load_dotenv()


class ZohoBookingsService:
    def __init__(self, zoho_auth):
        self.api_url = os.getenv("API_URL")
        self.zoho_auth = zoho_auth
        self.access_token = self.zoho_auth.get_access_token()

    def get_headers(self):
        print("access token", self.access_token)
        if not self.access_token:
            self.access_token = self.zoho_auth.get_access_token()
        return {
            "Authorization": f"Zoho-oauthtoken {self.access_token}",
            "Content-Type": "application/json",
        }

    def get_workspaces(self, workspace_id=None):
        print("entrando")
        url = f"{self.api_url}/workspaces"
        if workspace_id:
            url += f"?workspace_id={workspace_id}"
        headers = self.get_headers()
        response = requests.get(url, headers=headers)
        print("respond", response.json())
        return response.json()
