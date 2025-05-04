import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.cloud import texttospeech, speech

# Berechtigungen für Google Calendar & Tasks
SCOPES = [
    "https://www.googleapis.com/auth/calendar",
    "https://www.googleapis.com/auth/calendar.events",
    "https://www.googleapis.com/auth/tasks"
]

class Authenticator:
    @staticmethod
    def authenticate(auth_type):
        creds = None
        script_dir = os.path.dirname(os.path.abspath(__file__))
        credentials_path = os.path.join(script_dir, 'credentials.json')
        token_path = os.path.join(script_dir, 'token.json')

        # === OAuth für Calendar & Tasks ===
        if auth_type in ["event", "todo"]:
            # Falls token.json existiert, laden
            if os.path.exists(token_path):
                creds = Credentials.from_authorized_user_file(token_path, SCOPES)

            # Token ist abgelaufen oder existiert nicht
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    # Versuch, das Token zu aktualisieren
                    try:
                        creds.refresh(Request())
                    except Exception as e:
                        print("Token-Refresh fehlgeschlagen:", str(e))
                        creds = None
                if not creds:
                    # Erneuter OAuth-Flow mit dauerhafter Berechtigung
                    try:
                        flow = InstalledAppFlow.from_client_secrets_file(
                            credentials_path, SCOPES)
                        creds = flow.run_local_server(
                            port=0,
                            access_type='offline',  # unbedingt nötig für Refresh-Token
                            prompt='consent'        # erzwingt neue Erlaubnis + Refresh-Token
                        )
                    except Exception as e:
                        print("OAuth-Authentifizierung fehlgeschlagen:", str(e))
                        return None

                # Speichern des neuen Tokens
                with open(token_path, "w") as token:
                    token.write(creds.to_json())

            # Passenden Google-Service zurückgeben
            if auth_type == "event":
                return build("calendar", "v3", credentials=creds)
            elif auth_type == "todo":
                return build("tasks", "v1", credentials=creds)

        # === Google Cloud Service Accounts (für TTS & STT) ===
        elif auth_type == "tts":
            try:
                service_key_path = os.path.join(script_dir, "service_key.json")
                os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = service_key_path
                return texttospeech.TextToSpeechClient()
            except Exception as e:
                print("TTS-Authentifizierung fehlgeschlagen:", str(e))
                return None

        elif auth_type == "stt":
            try:
                service_key_path = os.path.join(script_dir, "service_key.json")
                os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = service_key_path
                return speech.SpeechClient()
            except Exception as e:
                print("STT-Authentifizierung fehlgeschlagen:", str(e))
                return None

        else:
            raise Exception("Ungültiger Authentifizierungs-Typ angegeben.")
