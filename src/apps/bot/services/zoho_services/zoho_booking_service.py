import json
import os

import requests
from dotenv import load_dotenv
from requests_toolbelt.multipart.encoder import MultipartEncoder


load_dotenv()


class ZohoBookingsService:
    def __init__(self, zoho_auth):
        self.api_url = os.getenv("API_URL")
        self.zoho_auth = zoho_auth
        self.access_token = self.zoho_auth.get_access_token()

    def get_headers(self):
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
        print("workspaces data", response.json())
        fetchappointment = self.fetch_appointments(
            service_id="4637313000000038020"
        )
        print("fetch appointment", fetchappointment)
        services = self.fetch_services("4637313000000038020")
        appointment = self.get_appointment(booking_id="AD-00002")
        print("fetching services", services)
        print("get appointment", appointment)
        return response.json()

    def fetch_appointments(
        self,
        service_id=None,
        staff_id=None,
        from_time=None,
        to_time=None,
        status=None,
        need_customer_more_info=None,
        customer_name=None,
        customer_email=None,
    ):
        url = f"{self.api_url}/fetchappointment"
        headers = self.get_headers()

        # Crear la estructura 'data' como un diccionario vacío
        data = {}

        # Solo agregar parámetros a 'data' si están definidos
        if service_id:
            data["service_id"] = service_id
        if staff_id:
            data["staff_id"] = staff_id
        if from_time:
            data["from_time"] = from_time
        if to_time:
            data["to_time"] = to_time
        if status:
            data["status"] = status
        if need_customer_more_info:
            data["need_customer_more_info"] = need_customer_more_info
        if customer_name:
            data["customer_name"] = customer_name
        if customer_email:
            data["customer_email"] = customer_email

        data_json = "{}" if not data else json.dumps(data)

        m = MultipartEncoder(
            fields={
                "data": (
                    None,
                    data_json,
                    "application/json",
                ),
            }
        )
        print("verificar m", m)

        headers["Content-Type"] = m.content_type

        response = requests.post(url, headers=headers, data=m)

        response.raise_for_status()

        return response.json()

    def fetch_services(self, workspace_id=None):
        url = f"{self.api_url}/services"
        headers = self.get_headers()
        if workspace_id:
            url += f"?workspace_id={workspace_id}"
        headers = self.get_headers()
        response = requests.get(url, headers=headers)
        print("respond", response.json())
        return response.json()

    def get_appointment(self, booking_id):
        url = f"{self.api_url}/getappointment"
        headers = self.get_headers()
        print("verify booking id", booking_id)
        if booking_id:
            url += f"?booking_id={booking_id}"
        headers = self.get_headers()
        print("test url", url)
        response = requests.get(url, headers=headers)
        print("appointment info", response.json())
        return response.json()
