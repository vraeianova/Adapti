import json
import os

import requests
from dotenv import load_dotenv
from requests_toolbelt.multipart.encoder import MultipartEncoder


load_dotenv()


class ZohoBookingsService:
    def __init__(self, zoho_auth):
        self.api_url = os.getenv("ZOHO_API_URL")
        self.zoho_auth = zoho_auth
        self.access_token = self.zoho_auth.get_access_token()

    def get_headers(self):
        if not self.access_token:
            self.access_token = self.zoho_auth.get_access_token()
        return {
            "Authorization": f"Zoho-oauthtoken {self.access_token}",
            "Content-Type": "application/json",
        }

    def fetch_workspaces(self, workspace_id=None):

        url = f"{self.api_url}/workspaces"

        if workspace_id:
            url += f"?workspace_id={workspace_id}"

        headers = self.get_headers()

        response = requests.get(url, headers=headers)

        response_json = response.json()

        workspace_data = (
            response_json.get("response", {})
            .get("returnvalue", {})
            .get("data", [])
        )

        if workspace_data:
            workspace_id = workspace_data[0].get("id")
            return workspace_id
        else:
            return "No puedo encontrar el workspace id"

    # TODO OPTIMIZAR FETCH APPOINTMENT
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
        data = {}
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
        headers["Content-Type"] = m.content_type
        response = requests.post(url, headers=headers, data=m)
        response.raise_for_status()
        return response.json()

    # TODO OPTIMIZAR GET APPOINTMENT
    def get_appointment(self, booking_id):
        url = f"{self.api_url}/getappointment"
        headers = self.get_headers()
        if booking_id:
            url += f"?booking_id={booking_id}"
        headers = self.get_headers()
        response = requests.get(url, headers=headers)
        return response.json()

    def fetch_staff(self, service_id=None, staff_id=None):
        url = f"{self.api_url}/staffs"
        headers = self.get_headers()

        # Si se proporcionan los parámetros opcionales, los añadimos a la URL.
        params = {}
        if staff_id:
            params["staff_id"] = staff_id
        if service_id:
            params["service_id"] = service_id

        # Verifica si hay parámetros que añadir a la URL.
        if params:
            query_string = "&".join(
                [f"{key}={value}" for key, value in params.items()]
            )
            url += f"?{query_string}"

        response = requests.get(url, headers=headers)
        response_json = response.json()

        staff_info = (
            response_json.get("response", {})
            .get("returnvalue", {})
            .get("data", [])
        )
        filtered_staff = [
            {
                "name": staff.get("name"),
                "additional_information": staff.get("additional_information"),
                "id": staff.get("id"),
            }
            for staff in staff_info
        ]

        # Devolver el resultado filtrado
        return {
            "data": filtered_staff,
            "status": response_json.get("response", {}).get("status"),
        }

    def fetch_services(self, workspace_id, staff_id=None, service_id=None):
        url = f"{self.api_url}/services?workspace_id={workspace_id}"
        headers = self.get_headers()

        # Si se proporcionan los parámetros opcionales, los añadimos a la URL.
        params = {}
        if staff_id:
            params["staff_id"] = staff_id
        if service_id:
            params["service_id"] = service_id

        # Verifica si hay parámetros adicionales para agregar a la URL.
        if params:
            query_string = "&".join(
                [f"{key}={value}" for key, value in params.items()]
            )
            url += f"&{query_string}"

        response = requests.get(url, headers=headers)
        response_json = response.json()

        # Filtra los datos importantes del servicio
        service_info = (
            response_json.get("response", {})
            .get("returnvalue", {})
            .get("data", [])
        )
        filtered_services = [
            {"name": service.get("name"), "id": service.get("id")}
            for service in service_info
        ]

        # Devuelve los servicios filtrados y el estado
        return {
            "data": filtered_services,
            "status": response_json.get("response", {}).get("status"),
        }

    def book_appointment(
        self,
        service_id,
        staff_id=None,
        group_id=None,
        from_time=None,
        to_time=None,
        time_zone=None,
        customer_details=None,
        notes=None,
        additional_fields=None,
    ):
        url = f"{self.api_url}/appointment"
        headers = self.get_headers()

        # Prepara los datos del formulario
        fields = {
            "service_id": service_id,
            "from_time": from_time,
            "customer_details": json.dumps(
                customer_details
            ),  # Se debe serializar como JSON
        }

        # Agrega los campos opcionales si se proporcionan
        if staff_id:
            fields["staff_id"] = staff_id
        if group_id:
            fields["group_id"] = group_id
        if to_time:
            fields["to_time"] = to_time
        if time_zone:
            fields["time_zone"] = time_zone
        if notes:
            fields["notes"] = notes
        if additional_fields:
            fields["additional_fields"] = json.dumps(additional_fields)

        # Usa MultipartEncoder para codificar los datos como multipart/form-data
        m = MultipartEncoder(fields=fields)
        headers["Content-Type"] = m.content_type

        # Realiza la solicitud POST
        response = requests.post(url, headers=headers, data=m)
        response_json = response.json()

        # Filtra solo los campos necesarios
        appointment_info = response_json.get("response", {}).get(
            "returnvalue", {}
        )
        filtered_info = {
            "service_name": appointment_info.get("service_name"),
            "staff_name": appointment_info.get("staff_name"),
            "start_time": appointment_info.get("start_time"),
        }

        # Devuelve los datos filtrados
        return {
            "data": filtered_info,
            "status": response_json.get("response", {}).get("status"),
        }

    def update_appointment(self, booking_id, action):
        if action not in ["completed", "cancel", "noshow"]:
            return {
                "status": "error",
                "message": "Invalid action. Action must be 'completed', 'canceled', or 'noshow'.",
            }

        url = f"{self.api_url}/updateappointment"

        headers = self.get_headers()
        fields = {
            "booking_id": booking_id,
            "action": action,
        }

        m = MultipartEncoder(fields=fields)
        headers["Content-Type"] = m.content_type

        response = requests.post(url, headers=headers, data=m)

        if response.status_code != 200:
            return {
                "status": "error",
                "message": "Failed to update the appointment. Please try again.",
            }

        response_json = response.json()

        # Procesar y devolver la información relevante
        appointment_info = response_json.get("response", {}).get(
            "returnvalue", {}
        )
        filtered_info = {
            "customer_info": appointment_info.get("customer_more_info"),
            "booked_on": appointment_info.get("booked_on"),
            "booking_status": appointment_info.get("status"),
        }

        return {
            "data": filtered_info,
            "status": response_json.get("response", {}).get("status"),
        }

    def fetch_availability(
        self,
        service_id,
        staff_id,
        selected_date,
        group_id=None,
        resource_id=None,
    ):

        url = f"{self.api_url}/availableslots"
        headers = self.get_headers()

        # Parámetros obligatorios y opcionales
        params = {
            "service_id": service_id,
            "staff_id": staff_id,
            "selected_date": selected_date,
        }

        # Añadir el campo requerido: staff_id, group_id, o resource_id
        if staff_id:
            params["staff_id"] = staff_id
        elif group_id:
            params["group_id"] = group_id
        elif resource_id:
            params["resource_id"] = resource_id
        else:
            raise ValueError(
                "Se requiere uno de los siguientes: staff_id, group_id o resource_id"
            )

        # Construir la URL con los parámetros opcionales
        if params:
            query_string = "&".join(
                [f"{key}={value}" for key, value in params.items()]
            )
            url += f"?{query_string}"

        response = requests.get(url, headers=headers)
        response_json = response.json()

        availability_info = (
            response_json.get("response", {})
            .get("returnvalue", {})
            .get("data", [])
        )

        # Formatear las horas disponibles como un string
        if availability_info:
            hours_string = ", ".join(availability_info)
            availability_message = (
                f"Las horas disponibles son: {hours_string}."
            )
        else:
            availability_message = (
                "No hay horas disponibles para la fecha seleccionada."
            )

        # Formatear la respuesta como un diccionario antes de enviarla
        formatted_response = {
            "data": availability_message,
            "status": response_json.get("response", {}).get("status", "error"),
        }

        # Devolver la respuesta formateada (sin json.dumps)
        return formatted_response
