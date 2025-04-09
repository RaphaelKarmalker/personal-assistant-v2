from pydantic import BaseModel, Field
from typing import List, Optional
from agents import Agent, function_tool, Runner
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import datetime
import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
import asyncio

# 🔑 Scopes für den Kalenderzugriff
SCOPES = ["https://www.googleapis.com/auth/calendar"]

def authenticate():
    print("TRY")
    creds = None
    script_dir = os.path.dirname(os.path.abspath(__file__))
    credentials_path = os.path.join(script_dir, 'credentials.json')

    # Token-Datei prüfen
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    # Wenn keine gültigen Anmeldeinformationen vorliegen
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            try:
                flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
                creds = flow.run_local_server(port=0, access_type='offline', prompt='consent')
            except Exception as e:
                print("Fehler bei der Authentifizierung:", str(e))
                return None
        # Token speichern
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    return creds

# 📅 Model für Erinnerungen
class ReminderModel(BaseModel):
    method: str = Field(..., description="Methode der Erinnerung (email, popup)")
    minutes: int = Field(..., description="Anzahl Minuten vor dem Ereignis")

# 📅 Model für Ereignis-Details
class EventDetails(BaseModel):
    summary: str = Field(..., description="Titel des Ereignisses")
    start_time: str = Field(..., description="Startzeit im ISO-Format (z.B. '2025-04-07T10:00:00')")
    end_time: str = Field(..., description="Endzeit im ISO-Format (z.B. '2025-04-07T11:00:00')")
    description: Optional[str] = Field(None, description="Beschreibung des Ereignisses")
    location: Optional[str] = Field(None, description="Veranstaltungsort")
    attendees: Optional[List[str]] = Field(None, description="Liste von E-Mail-Adressen der Teilnehmer")
    reminders: Optional[List[ReminderModel]] = Field(None, description="Liste von Erinnerungen")
    recurrence: Optional[List[str]] = Field(None, description="Wiederholung des Ereignisses")
    color_id: Optional[int] = Field(None, description="Farb-ID zur Kategorisierung")

# 📅 Model für Ereignis-Liste-Parameter
class EventListParams(BaseModel):
    start_time: str = Field(..., description="Startzeit des Zeitraums im ISO-Format")
    end_time: str = Field(..., description="Endzeit des Zeitraums im ISO-Format")
    max_results: Optional[int] = Field(None, description="Maximale Anzahl der anzuzeigenden Ereignisse")
    color_id: Optional[int] = Field(None, description="Farb-ID zum Filtern der Ereignisse")
    title: Optional[str] = Field(None, description="Stichwort im Titel zum Filtern")

# 📅 Model für Ereignis-Löschparameter
class DeleteEventParams(BaseModel):
    search_name: str = Field(..., description="Teil des Titels des zu löschenden Ereignisses")
    start_time: str = Field(..., description="Startzeit des Suchzeitraums im ISO-Format")
    end_time: str = Field(..., description="Endzeit des Suchzeitraums im ISO-Format")

# 📅 Model für Ereignis-Modifikationsparameter
class ModifyEventParams(BaseModel):
    search_name: str = Field(..., description="Teil des Titels des zu ändernden Ereignisses")
    start_time: str = Field(..., description="Startzeit des Suchzeitraums im ISO-Format")
    end_time: str = Field(..., description="Endzeit des Suchzeitraums im ISO-Format")
    new_summary: Optional[str] = Field(None, description="Neuer Titel des Ereignisses")
    new_start_time: Optional[str] = Field(None, description="Neue Startzeit im ISO-Format")
    new_end_time: Optional[str] = Field(None, description="Neue Endzeit im ISO-Format")
    new_description: Optional[str] = Field(None, description="Neue Beschreibung des Ereignisses")
    new_location: Optional[str] = Field(None, description="Neuer Veranstaltungsort")
    new_attendees: Optional[List[str]] = Field(None, description="Liste neuer E-Mail-Adressen der Teilnehmer")
    new_reminders: Optional[List[ReminderModel]] = Field(None, description="Liste neuer Erinnerungen")
    new_recurrence: Optional[List[str]] = Field(None, description="Neue Wiederholung des Ereignisses")
    new_color_id: Optional[int] = Field(None, description="Neue Farb-ID zur Kategorisierung")

@function_tool
def modify_event(params: ModifyEventParams) -> str:
    """
    Ändert ein bestehendes Ereignis im Google Kalender basierend auf einem Suchbegriff im Titel und einem Zeitraum.
    """
    creds = authenticate()
    if not creds:
        return "Authentifizierung fehlgeschlagen."

    service = build("calendar", "v3", credentials=creds)

    try:
        start_time = params.start_time + "Z"
        end_time = params.end_time + "Z"

        # Suche nach dem passenden Ereignis
        events_result = service.events().list(
            calendarId='primary',
            timeMin=start_time,
            timeMax=end_time,
            singleEvents=True,
            orderBy="startTime"
        ).execute()

        events = events_result.get("items", [])

        for event in events:
            if params.search_name.lower() in event.get("summary", "").lower():
                # Event gefunden: Aktualisierung vorbereiten
                updated_event = event.copy()

                if params.new_summary:
                    updated_event['summary'] = params.new_summary
                if params.new_start_time:
                    updated_event['start'] = {'dateTime': params.new_start_time, 'timeZone': 'Europe/Berlin'}
                if params.new_end_time:
                    updated_event['end'] = {'dateTime': params.new_end_time, 'timeZone': 'Europe/Berlin'}
                if params.new_description:
                    updated_event['description'] = params.new_description
                if params.new_location:
                    updated_event['location'] = params.new_location
                if params.new_attendees:
                    updated_event['attendees'] = [{'email': attendee} for attendee in params.new_attendees]
                if params.new_reminders:
                    updated_event['reminders'] = {
                        'useDefault': False,
                        'overrides': [{'method': r.method, 'minutes': r.minutes} for r in params.new_reminders]
                    }
                if params.new_recurrence:
                    updated_event['recurrence'] = params.new_recurrence
                if params.new_color_id:
                    updated_event['colorId'] = str(params.new_color_id)

                # Aktualisiere das Event im Kalender
                updated_event = service.events().update(
                    calendarId='primary',
                    eventId=event['id'],
                    body=updated_event,
                    sendUpdates='all'
                ).execute()

                return f"Ereignis '{updated_event['summary']}' erfolgreich aktualisiert: {updated_event.get('htmlLink')}"

        return "Kein passendes Ereignis gefunden."
    except HttpError as error:
        return f"Fehler beim Ändern des Ereignisses: {error}"


@function_tool
def get_current_time(format: Optional[str] = None) -> str:
    """
    Gibt das aktuelle Datum und die Uhrzeit zurück.
    
    Args:
        format: Format des Datums und der Uhrzeit im strftime-Stil. 
                Beispiel: "%Y-%m-%d %H:%M:%S" (Datum und Uhrzeit).
    
    Returns:
        Die aktuelle Uhrzeit oder das Datum im angegebenen Format.
    """
    try:
        # Wenn kein Format angegeben ist, verwende Standardformat für Datum und Uhrzeit
        if format is None or format.strip() == "":
            format = "%Y-%m-%d %H:%M:%S"
        current_date = datetime.datetime.now().strftime(format)
        #print(current_date)
        return current_date
    except Exception as e:
        #print(f"Fehler beim Formatieren der Uhrzeit: {str(e)}")
        return f"Fehler beim Formatieren der Uhrzeit: {str(e)}"


@function_tool
def create_final_event(event: EventDetails) -> str:
    """
    Erstellt ein neues Ereignis im Google Kalender.
    """
    creds = authenticate()
    if not creds:
        return "Authentifizierung fehlgeschlagen."

    service = build("calendar", "v3", credentials=creds)

    try:
        event_body = {
            'summary': event.summary,
            'start': {'dateTime': event.start_time, 'timeZone': 'Europe/Berlin'},
            'end': {'dateTime': event.end_time, 'timeZone': 'Europe/Berlin'}
        }

        if event.description:
            event_body['description'] = event.description
        if event.location:
            event_body['location'] = event.location
        if event.attendees:
            event_body['attendees'] = [{'email': attendee} for attendee in event.attendees]

        created_event = service.events().insert(
            calendarId='primary',
            body=event_body,
            sendUpdates='all'
        ).execute()

        return f"Ereignis erfolgreich erstellt: {created_event.get('htmlLink')}"
    except HttpError as error:
        return f"Fehler beim Erstellen des Ereignisses: {error}"

@function_tool
def list_events(params: EventListParams) -> str:
    """
    Listet Ereignisse im angegebenen Zeitraum auf, optional gefiltert nach Farbe, Titel und Anzahl.
    """
    creds = authenticate()
    if not creds:
        return "Authentifizierung fehlgeschlagen."

    service = build("calendar", "v3", credentials=creds)

    try:
        start_time = params.start_time + "Z"
        end_time = params.end_time + "Z"
        max_results = params.max_results if params.max_results else 10

        events_result = service.events().list(
            calendarId='primary',
            timeMin=start_time,
            timeMax=end_time,
            maxResults=max_results,
            singleEvents=True,
            orderBy="startTime"
        ).execute()

        events = events_result.get("items", [])

        if not events:
            return "Keine Ereignisse gefunden."

        event_list = [f"- {event['start'].get('dateTime', event['start'].get('date'))} | {event['summary']}" for event in events]
        return "\n".join(event_list)
    except HttpError as error:
        return f"Fehler beim Abrufen der Ereignisse: {error}"

@function_tool
def delete_event(params: DeleteEventParams) -> str:
    """
    Löscht ein Ereignis im Google Kalender basierend auf einem Suchbegriff im Titel und einem Zeitraum.
    """
    creds = authenticate()
    if not creds:
        return "Authentifizierung fehlgeschlagen."

    service = build("calendar", "v3", credentials=creds)

    try:
        start_time = params.start_time + "Z"
        end_time = params.end_time + "Z"

        events_result = service.events().list(
            calendarId='primary',
            timeMin=start_time,
            timeMax=end_time,
            singleEvents=True,
            orderBy="startTime"
        ).execute()

        events = events_result.get("items", [])

        for event in events:
            if params.search_name.lower() in event.get("summary", "").lower():
                service.events().delete(calendarId='primary', eventId=event['id'], sendUpdates='all').execute()
                return f"Ereignis '{event['summary']}' erfolgreich gelöscht."
        return "Kein passendes Ereignis gefunden."
    except HttpError as error:
        return f"Fehler beim Löschen des Ereignisses: {error}"

# 💡 Agenten-Setup
appointment_agent = Agent(
    name="Termin Agent",
    instructions="Agent zur Erstellung, Auflistung, Änderung und Löschung von Terminen.",
    tools=[create_final_event, list_events, get_current_time, delete_event, modify_event],
    model="gpt-4o"
)

# 🌟 Kontextverwaltung
context = []

def update_context(role, message):
    context.append({"role": role, "content": message})
    if len(context) > 10:
        context.pop(0)

def get_context_summary():
    summary = "\n".join([f"{entry['role']}: {entry['content']}" for entry in context])
    return f"Kontext:\n{summary}"

async def run_agent():
    print("Termin Agent gestartet. Du kannst jederzeit mit 'exit' beenden.")
    while True:
        user_input = input("Du: ")
        if user_input.lower() in ["exit", "quit"]:
            print("Agent beendet. Bis bald!")
            break

        # Kontext aktualisieren
        update_context("User", user_input)

        try:
            # Kontext zusammenstellen
            context_summary = get_context_summary()
            full_input = f"{context_summary}\n\nUser: {user_input}"
            
            # Agentenaufruf mit Kontext
            result = await Runner.run(appointment_agent, full_input)
            output = str(result.final_output)
            print(f"Ergebnis: {output}")

            # Kontext aktualisieren
            update_context("Bot", output)

        except Exception as e:
            print(f"Fehler: {e}")


if __name__ == "__main__":
    asyncio.run(run_agent())
