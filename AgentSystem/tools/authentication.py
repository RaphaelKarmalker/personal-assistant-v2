import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.cloud import texttospeech, speech

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
        token_path = os.path.join(script_dir, 'token.json')

        # OAuth-basierte Dienste
        if type in ["event", "todo"]:
            if os.path.exists(token_path):
                creds = Credentials.from_authorized_user_file(token_path, SCOPES)

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
                with open(token_path, "w") as token:
                    token.write(creds.to_json())

            if type == "event":
                return build("calendar", "v3", credentials=creds)
            elif type == "todo":
                return build("tasks", "v1", credentials=creds)

        # Service-Account-basierte Dienste
        elif type == "tts":
            try:
                service_key_path = os.path.join(script_dir, "service_key.json")
                os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = service_key_path
                return texttospeech.TextToSpeechClient()
            except Exception as e:
                print("TTS authentication failed:", str(e))
                return None

        elif type == "stt":
            try:
                service_key_path = os.path.join(script_dir, "service_key.json")
                os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = service_key_path
                return speech.SpeechClient()
            except Exception as e:
                print("STT authentication failed:", str(e))
                return None

        else:
            raise Exception("Keine gültige Authentifizierung gefunden.")
