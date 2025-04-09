import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = [
    "https://www.googleapis.com/auth/calendar",
    "https://www.googleapis.com/auth/calendar.events",
    "https://www.googleapis.com/auth/tasks"
]


class Authenticator:
    @staticmethod
    def authenticate(type):
        creds = None
        script_dir = os.path.dirname(os.path.abspath(__file__))
        credentials_path = os.path.join(script_dir, 'credentials.json')

        if os.path.exists("token.json"):
            creds = Credentials.from_authorized_user_file("token.json", SCOPES)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                try:
                    flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
                    creds = flow.run_local_server(port=0, access_type='offline', prompt='consent')
                except Exception as e:
                    print("Authentication failed:", str(e))
                    return None
            with open("token.json", "w") as token:
                token.write(creds.to_json())
        if type == "event":
            return build("calendar", "v3", credentials=creds)
        elif type == "todo":
            return build("tasks", "v1", credentials=creds)
        else:
            raise Exception("Keine gültige Authentifizierung gefunden.")
