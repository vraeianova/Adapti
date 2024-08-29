import os

from apps.zoho.services import ZohoAuth, ZohoBookingsService


class ZohoConfig:
    def __init__(
        self,
        client_id=None,
        client_secret=None,
        redirect_uri=None,
        account_url=None,
        authorization_code=None,
    ):
        self.client_id = client_id or os.getenv("ZOHO_CLIENT_ID")
        self.client_secret = client_secret or os.getenv("ZOHO_CLIENT_SECRET")
        self.redirect_uri = redirect_uri or os.getenv("ZOHO_REDIRECT_URI")
        self.account_url = account_url or os.getenv("ZOHO_ACCOUNT_URL")
        self.authorization_code = authorization_code or os.getenv(
            "ZOHO_AUTHORIZATION_CODE"
        )  # Inject authorization code

    def get_zoho_auth(self):
        return ZohoAuth(
            client_id=self.client_id,
            client_secret=self.client_secret,
            redirect_uri=self.redirect_uri,
            account_url=self.account_url,
            authorization_code=self.authorization_code,  # Pass it to ZohoAuth
        )

    def get_zoho_bookings_service(self):
        zoho_auth = self.get_zoho_auth()
        return ZohoBookingsService(zoho_auth=zoho_auth)
