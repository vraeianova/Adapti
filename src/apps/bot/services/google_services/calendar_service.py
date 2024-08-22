import datetime

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


class GoogleCalendarService:
    def __init__(self, credentials):
        """
        Inicializa el servicio de Google Calendar con las credenciales autenticadas.
        :param credentials: Credenciales de OAuth2 obtenidas tras la autenticación.
        """
        self.service = build("calendar", "v3", credentials=credentials)

    def list_events(self, max_results=10):
        """
        Lista los próximos eventos en el calendario principal del usuario.
        :param max_results: Número máximo de eventos a devolver.
        :return: Lista de eventos.
        """
        try:
            now = (
                datetime.datetime.utcnow().isoformat() + "Z"
            )  # 'Z' indica UTC time
            events_result = (
                self.service.events()
                .list(
                    calendarId="primary",
                    timeMin=now,
                    maxResults=max_results,
                    singleEvents=True,
                    orderBy="startTime",
                )
                .execute()
            )
            events = events_result.get("items", [])

            if not events:
                print("No upcoming events found.")
                return []

            for event in events:
                start = event["start"].get(
                    "dateTime", event["start"].get("date")
                )
                print(start, event["summary"])

            return events

        except HttpError as error:
            print(f"An error occurred: {error}")
            return []

    def create_event(
        self,
        summary,
        start_time,
        end_time,
        description=None,
        location=None,
        attendees=None,
    ):
        """
        Crea un evento en el calendario principal del usuario.
        :param summary: Título del evento.
        :param start_time: Hora de inicio en formato RFC3339.
        :param end_time: Hora de finalización en formato RFC3339.
        :param description: Descripción del evento.
        :param location: Ubicación del evento.
        :param attendees: Lista de asistentes (correos electrónicos).
        :return: Evento creado.
        """
        event = {
            "summary": summary,
            "location": location,
            "description": description,
            "start": {
                "dateTime": start_time,
                "timeZone": "UTC",
            },
            "end": {
                "dateTime": end_time,
                "timeZone": "UTC",
            },
            "attendees": (
                [{"email": email} for email in attendees] if attendees else []
            ),
        }

        try:
            event = (
                self.service.events()
                .insert(calendarId="primary", body=event)
                .execute()
            )
            print(f'Event created: {event.get("htmlLink")}')
            return event

        except HttpError as error:
            print(f"An error occurred: {error}")
            return None

    def update_event(
        self,
        event_id,
        summary=None,
        start_time=None,
        end_time=None,
        description=None,
        location=None,
        attendees=None,
    ):
        """
        Actualiza un evento existente en el calendario principal del usuario.
        :param event_id: ID del evento a actualizar.
        :param summary: Título del evento.
        :param start_time: Hora de inicio en formato RFC3339.
        :param end_time: Hora de finalización en formato RFC3339.
        :param description: Descripción del evento.
        :param location: Ubicación del evento.
        :param attendees: Lista de asistentes (correos electrónicos).
        :return: Evento actualizado.
        """
        try:
            event = (
                self.service.events()
                .get(calendarId="primary", eventId=event_id)
                .execute()
            )

            if summary:
                event["summary"] = summary
            if start_time:
                event["start"] = {"dateTime": start_time, "timeZone": "UTC"}
            if end_time:
                event["end"] = {"dateTime": end_time, "timeZone": "UTC"}
            if description:
                event["description"] = description
            if location:
                event["location"] = location
            if attendees:
                event["attendees"] = [{"email": email} for email in attendees]

            updated_event = (
                self.service.events()
                .update(calendarId="primary", eventId=event_id, body=event)
                .execute()
            )
            print(f'Event updated: {updated_event.get("htmlLink")}')
            return updated_event

        except HttpError as error:
            print(f"An error occurred: {error}")
            return None

    def delete_event(self, event_id):
        """
        Elimina un evento del calendario principal del usuario.
        :param event_id: ID del evento a eliminar.
        :return: None.
        """
        try:
            self.service.events().delete(
                calendarId="primary", eventId=event_id
            ).execute()
            print(f"Event deleted: {event_id}")
        except HttpError as error:
            print(f"An error occurred: {error}")
