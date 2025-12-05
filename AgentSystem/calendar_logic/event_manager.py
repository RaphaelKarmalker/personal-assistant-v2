from tools.authentication import Authenticator
from calendar_logic.models import EventDetails, ModifyEventParams, EventListParams, DeleteEventParams, ReminderModel
from typing import Optional
from googleapiclient.errors import HttpError
from datetime import datetime


class EventManager:
    def __init__(self):
        # Authenticate and initialize the Google Calendar service
        self.service = Authenticator.authenticate("event")

    def modify_event(self, params: ModifyEventParams) -> str:
        try:
            # Format the start and end times for the event search
            start_time = params.start_time + "Z"
            end_time = params.end_time + "Z"

            # Search for the matching event
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
                    # Event found: Prepare for update
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

                    # Update the event in Google Calendar
                    updated_event = self.service.events().update(
                        calendarId='primary',
                        eventId=event['id'],
                        body=updated_event,
                        sendUpdates='all'
                    ).execute()

                    return f"Event '{updated_event['summary']}' updated successfully."

            return "No matching event found."
        except HttpError as error:
            return f"Error while modifying the event: {error}"

    def get_current_time(self, format: Optional[str] = None) -> str:
        """
        Returns the current date and time.
        
        Args:
            format: Format of the date and time in strftime style. 
                    Example: "%Y-%m-%d %H:%M:%S" (date and time).
        
        Returns:
            The current time or date in the specified format.
        """
        try:
            # If no format is specified, use the default format for date and time
            if format is None or format.strip() == "":
                format = "%Y-%m-%d %H:%M:%S"
            current_date = datetime.datetime.now().strftime(format)
            #print(current_date)
            return current_date
        except Exception as e:
            #print(f"Error formatting the time: {str(e)}")
            return f"Error formatting the time: {str(e)}"
        


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

            return f"Event created successfully: {created_event.get('htmlLink')}"
        except HttpError as error:
            return f"Error creating the event: {error}"

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
                return "No events found."

            event_list = [f"- {event['start'].get('dateTime', event['start'].get('date'))} | {event['summary']}" for event in events]
            return "\n".join(event_list)
        except HttpError as error:
            return f"Error retrieving events: {error}"

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
                    return f"Event '{event['summary']}' deleted successfully."
            return "No matching event found."
        except HttpError as error:
            return f"Error deleting the event: {error}"