### agent/agent_runner.py
from agents import Agent, function_tool, Runner
from calendar_logic.event_manager import EventManager
from calendar_logic.models import EventDetails, ModifyEventParams, EventListParams, DeleteEventParams
from tools.context_manager import ContextManager
from typing import Optional
import datetime

# Initialisiere den EventManager
event_manager = EventManager()
context_manager = ContextManager()

@function_tool
def create_final_event(event: EventDetails) -> str:
    """
    Erstellt ein neues Ereignis im Google Kalender. Darauf achten das aktuelle Datum als Referenz zu verwenden!
    """
    return event_manager.create_final_event(event)

@function_tool
def modify_existing_event(params: ModifyEventParams) -> str:
    """
    Ändert ein bestehendes Ereignis im Google Kalender basierend auf einem Suchbegriff im Titel und einem Zeitraum.
    """
    return event_manager.modify_event(params)

@function_tool
def delete_event(params: DeleteEventParams) -> str:
    """
    Löscht ein Ereignis im Google Kalender basierend auf einem Suchbegriff im Titel und einem Zeitraum.
    """
    return event_manager.delete_event(params)

@function_tool
def list_events(params: EventListParams) -> str:
    """
    Listet Ereignisse im angegebenen Zeitraum auf, optional gefiltert nach Farbe, Titel und Anzahl.
    """

    return event_manager.list_events(params)

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

appointment_agent = Agent(
    name="Termin Agent",
    instructions=("Agent zur Erstellung, Auflistung, Änderung und Löschung von Terminen." 
            "Achte auf die Verwendung des aktuellen Datums bei Terminen."
            "Trage den termin erst endgültig ein wenn du terminname und Uhrzeit hast."),           
    handoff_description="Agent for handling appointments and reminders.",
    tools=[create_final_event, modify_existing_event, delete_event, list_events, get_current_time],
    model="gpt-4o"
)

async def run_agent_termin():
    print("Termin Agent gestartet. Du kannst jederzeit mit 'exit' beenden.")
    while True:
        user_input = input("Du: ")
        if user_input.lower() in ["exit", "quit"]:
            print("Agent beendet. Bis bald!")
            break

        # Kontext aktualisieren
        

        try:
            # Kontext zusammenstellen
            context_summary = context_manager.get_context_summary()
            full_input = f"History: {context_summary}\n\nNew Input: {user_input}"

            # Agentenaufruf mit Kontext
            result = await Runner.run(appointment_agent, full_input)
            output = str(result.final_output)
            print(f"Ergebnis: {output}")

            # Kontext aktualisieren
            context_manager.update_context("User", user_input)
            context_manager.update_context("Assistant", output)

        except Exception as e:
            print(f"Fehler: {e}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(run_agent_termin())
