import os

from django.conf import settings
from django.shortcuts import redirect
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build


class GoogleCalendarClient:
    SCOPES = ["https://www.googleapis.com/auth/calendar"]
    redirect_uri = "http://localhost:8000/api/v1/bot/oauth2callback/"

    def __init__(
        self,
        credentials_file="avaantyCredentials.json",
        token_file="token.json",
    ):
        self.creds = None
        self.credentials_file = self._get_credentials_path(credentials_file)
        self.token_file = token_file
        self.authenticate()

    def _get_credentials_path(self, credentials_file):
        """
        Verifica y devuelve la ruta del archivo de credenciales.
        :param credentials_file: Nombre del archivo de credenciales.
        :return: Ruta completa del archivo de credenciales.
        """
        # Si el archivo de credenciales está en el directorio base del proyecto
        credentials_path = os.path.join(settings.BASE_DIR, credentials_file)
        print("verificar credenciales", credentials_path)
        if os.path.exists(credentials_path):
            return credentials_path

        # Si el archivo de credenciales está un directorio por encima del directorio base
        credentials_path = os.path.join(
            os.path.abspath(os.path.join(settings.BASE_DIR, os.pardir)),
            credentials_file,
        )
        print("verificr credentials path", credentials_path)
        if os.path.exists(credentials_path):
            return credentials_path

        # Si el archivo no se encuentra en ninguna de las rutas esperadas, lanzar un error
        raise FileNotFoundError(
            f"No se encontró el archivo de credenciales: {credentials_file}"
        )

    def authenticate(self):
        """
        Autentica al usuario utilizando OAuth2. Carga las credenciales guardadas o inicia un nuevo flujo de autenticación.
        """
        self.load_saved_credentials()

        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                print("entro a refresh token")
                self.refresh_access_token()
            else:
                print("inicio flujo de autenticacion")
                self.start_auth_flow()
            self.save_credentials()

    def load_saved_credentials(self):
        """
        Carga las credenciales guardadas desde el archivo token.json si existen.
        """
        print("entro a load saved credentials")
        if os.path.exists(self.token_file):
            self.creds = Credentials.from_authorized_user_file(
                self.token_file, self.SCOPES
            )

    def refresh_access_token(self):
        """
        Refresca el token de acceso si el token ha expirado y existe un refresh token.
        """
        self.creds.refresh(Request())

    def start_auth_flow(self, redirect_uri=redirect_uri):
        """
        Inicia un nuevo flujo de autenticación OAuth2 si no hay credenciales válidas.
        :param redirect_uri: URI de redirección para el flujo OAuth2.
        """
        print("Iniciando flujo de autenticación")
        flow = InstalledAppFlow.from_client_secrets_file(
            self.credentials_file, self.SCOPES
        )
        print("mira mi flow", flow)
        if redirect_uri:
            print("tengo redireccion", redirect_uri)
            flow.redirect_uri = redirect_uri

        print("A punto de abrir el servidor local")
        print("verificar que uri tengo en flow", flow.redirect_uri)
        self.creds = flow.run_local_server(port=9000)

    def save_credentials(self):
        """
        Guarda las credenciales actuales en un archivo token.json.
        """
        print("token")
        with open(self.token_file, "w") as token:
            token.write(self.creds.to_json())

    def get_service(self):
        """
        Crea y devuelve un servicio de Google Calendar autenticado.
        :return: Objeto de servicio de Google Calendar.
        """
        return build("calendar", "v3", credentials=self.creds)
