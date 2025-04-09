from agents import Agent, InputGuardrail, GuardrailFunctionOutput, Runner
from pydantic import BaseModel
import asyncio


import datetime
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from agents import FunctionTool, function_tool

# Scopes für den Kalenderzugriff



def authenticate():
    SCOPES = ["https://www.googleapis.com/auth/calendar"]
    creds = None
    script_dir = os.path.dirname(os.path.abspath(__file__))
    credentials_path = os.path.join(script_dir, 'credentials.json')

    # Überprüfen, ob ein Token existiert
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
        # Speichern der Anmeldeinformationen
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    return creds

@function_tool
def create_final_event(summary, start_time, end_time, 
                 description=None, location=None, timezone="UTC", 
                 attendees=None, reminders=None, recurrence=None):
    creds = authenticate()
    if not creds:
        print("Authentifizierung fehlgeschlagen.")
        return
    service = build("calendar", "v3", credentials=creds)
    """
    Erstellt ein neues Ereignis im Google Kalender. Nur erstellen wenn vom Nutzer explizit aufgefordert.
    Args:
        service: Der authentifizierte Kalenderdienst
        summary: Titel des Ereignisses
        start_time: Startzeit im ISO-Format (z.B. '2025-04-07T10:00:00')
        end_time: Endzeit im ISO-Format (z.B. '2025-04-07T11:00:00')
        description: (optional) Beschreibung des Ereignisses
        location: (optional) Veranstaltungsort
        timezone: (optional) Zeitzone, Standard: 'UTC'
        attendees: (optional) Liste von E-Mail-Adressen der Teilnehmer
        reminders: (optional) Liste von Erinnerungen im Format [{'method': 'email', 'minutes': 10}]
        recurrence: (optional) Wiederholung, z.B. ['RRULE:FREQ=DAILY;COUNT=5']
    """
    try:
        event = {
            'summary': summary,
            'location': location,
            'description': description,
            'start': {
                'dateTime': start_time,
                'timeZone': timezone,
            },
            'end': {
                'dateTime': end_time,
                'timeZone': timezone,
            },
            'attendees': [{'email': attendee} for attendee in attendees] if attendees else [],
            'reminders': {
                'useDefault': False,
                'overrides': reminders if reminders else [
                    {'method': 'email', 'minutes': 10},
                    {'method': 'popup', 'minutes': 5},
                ],
            },
            'recurrence': recurrence if recurrence else []
        }

        created_event = service.events().insert(
            calendarId='primary',
            body=event
        ).execute()

        print(f"Ereignis erstellt: {created_event.get('htmlLink')}")
    except HttpError as error:
        print(f"Fehler beim Erstellen des Ereignisses: {error}")



# Pydantic-Modelle für strukturierte Ausgaben
class ToDo(BaseModel):
    title: str
    deadline: str
    time: str

class Reminder(BaseModel):
    reminder_text: str
    date: str
    time: str

class Appointment(BaseModel):
    title: str
    date: str
    time: str

# Handoff-Entscheidungsmodell
class HandoffOutput(BaseModel):
    agent_name: str
    reasoning: str

# Guardrail Agent: Entscheidungshilfe für den Handoff
guardrail_agent = Agent(
    name="Guardrail Check",
    instructions="Analyze the user's input and determine which specialized agent is needed: To-Do, Reminder, or Appointment.",
    output_type=HandoffOutput,
    model="gpt-4o"
)

# Spezialagenten
todo_agent = Agent(
    name="To-Do Agent",
    handoff_description="Agent for managing to-do tasks",
    instructions=(
        "Erstelle eine To-Do-Aufgabe. "
        "Wenn die Eingabe eine Ergänzung oder Änderung zu einer bestehenden Aufgabe ist, "
        "nutze die zuletzt erstellte oder genannte To-Do-Aufgabe als Referenz. "
        "Frage nach, wenn die Eingabe unklar ist."
    ),
    model="gpt-4o"
)

reminder_agent = Agent(
    name="Reminder Agent",
    handoff_description="Agent for setting reminders",
    instructions=(
        "Setze eine Erinnerung. "
        "Wenn die Eingabe eine Ergänzung oder Änderung zu einer bestehenden Erinnerung ist, "
        "nutze die zuletzt erstellte oder genannte Erinnerung als Referenz. "
        "Frage nach, wenn die Eingabe unklar ist."
    ),
    model="gpt-4o"
)

appointment_agent = Agent(
    name="Termin Agent",
    handoff_description="Agent for creating appointments.",
    tools=[create_final_event],
    instructions=(
        "Erstelle einen Termin. Wenn die Eingabe eine Ergänzung oder Änderung zu einem bestehenden Termin ist, "
        "nutze den zuletzt erstellten oder genannten Termin als Referenz. "
        "Frage nach, wenn die Eingabe unklar ist."
    ),
    model="gpt-4o"
)

# Kontextverwaltung: Letzte Nachrichten zusammenfassen
def create_context_summary(context):
    summary = " ".join([entry["content"] for entry in context[-5:]])  # Letzte 5 Nachrichten
    return f"Historie: {summary}"

# Guardrail-Funktion zur dynamischen Auswahl des spezialisierten Agents
async def handoff_guardrail(ctx, agent, input_data):
    result = await Runner.run(guardrail_agent, input_data)
    final_output = result.final_output_as(HandoffOutput)
    if final_output.agent_name:
        return GuardrailFunctionOutput(
            output_info=final_output,
            tripwire_triggered=False,
        )
    return GuardrailFunctionOutput(
        output_info=final_output,
        tripwire_triggered=True,
    )

# Handoff Agent mit dynamischer Agentenauswahl
triage_agent = Agent(
    name="Triage Agent",
    instructions=(
        "Analyze the input and hand off to the appropriate specialized agent: To-Do, Reminder, or Appointment. "
        "Always consider the previous context when processing the current input. "
        #"If the user provides additional details or modifies a previous task, combine it with the last context."
    ),
    handoffs=[todo_agent, reminder_agent, appointment_agent],
)

# Hauptschleife zur Eingabe
async def run_handoff():
    print("Handoff Agent gestartet. Du kannst jederzeit mit 'exit' beenden.")

    # Kontext initialisieren
    context = []

    while True:
        user_input = input("Du: ")
        if user_input.lower() in ["exit", "quit"]:
            print("Handoff Agent beendet. Bis bald!")
            break

        # Eingabe dem Kontext hinzufügen
        context.append({"role": "user", "content": user_input})

        try:
            # Kontext zusammenfassen und der Eingabe voranstellen
            context_summary = create_context_summary(context)
            full_input = f"{context_summary} {user_input}"

            # Läuft den Agenten mit der kombinierten Eingabe
            result = await Runner.run(triage_agent, full_input)
            print(f"Ergebnis: {result.final_output}")

            # Kontext aktualisieren: Antwort dem Kontext hinzufügen
            context.append({"role": "assistant", "content": str(result.final_output)})

        except Exception as e:
            print(f"Fehler während der Agentenausführung: {e}")

# Starte die asynchrone Schleife
if __name__ == "__main__":
    asyncio.run(run_handoff())
