from tools.authentication import Authenticator
from calendar_logic.models import EventDetails, ModifyEventParams, EventListParams, DeleteEventParams, ReminderModel
from typing import Optional
from googleapiclient.errors import HttpError
from datetime import datetime


class EventManager:
    def __init__(self):
        self.service = Authenticator.authenticate("event")

    def modify_event(self, params: ModifyEventParams) -> str:
        try:
            start_time = params.start_time + "Z"
            end_time = params.end_time + "Z"

            # Suche nach dem passenden Ereignis
            events_result = self.service.events().list(
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
                    updated_event = self.service.events().update(
                        calendarId='primary',
                        eventId=event['id'],
                        body=updated_event,
                        sendUpdates='all'
                    ).execute()

                    return f"Ereignis '{updated_event['summary']}' erfolgreich aktualisiert: {updated_event.get('htmlLink')}"

            return "Kein passendes Ereignis gefunden."
        except HttpError as error:
            return f"Fehler beim Ändern des Ereignisses: {error}"

    def get_current_time(self, format: Optional[str] = None) -> str:
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
        


    def create_final_event(self, event: EventDetails) -> str:
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

            created_event = self.service.events().insert(
                calendarId='primary',
                body=event_body,
                sendUpdates='all'
            ).execute()

            return f"Ereignis erfolgreich erstellt: {created_event.get('htmlLink')}"
        except HttpError as error:
            return f"Fehler beim Erstellen des Ereignisses: {error}"

    def list_events(self, params: EventListParams) -> str:

        try:
            start_time = params.start_time + "Z"
            end_time = params.end_time + "Z"
            max_results = params.max_results if params.max_results else 10

            events_result = self.service.events().list(
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

    def delete_event(self, params: DeleteEventParams) -> str:

        try:
            start_time = params.start_time + "Z"
            end_time = params.end_time + "Z"

            events_result = self.service.events().list(
                calendarId='primary',
                timeMin=start_time,
                timeMax=end_time,
                singleEvents=True,
                orderBy="startTime"
            ).execute()

            events = events_result.get("items", [])

            for event in events:
                if params.search_name.lower() in event.get("summary", "").lower():
                    self.service.events().delete(calendarId='primary', eventId=event['id'], sendUpdates='all').execute()
                    return f"Ereignis '{event['summary']}' erfolgreich gelöscht."
            return "Kein passendes Ereignis gefunden."
        except HttpError as error:
            return f"Fehler beim Löschen des Ereignisses: {error}"