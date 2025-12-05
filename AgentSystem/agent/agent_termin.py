### agent/agent_runner.py
from agents import Agent, function_tool, Runner
from calendar_logic.event_manager import EventManager
from calendar_logic.models import EventDetails, ModifyEventParams, EventListParams, DeleteEventParams
from tools.context_manager import ContextManager
from typing import Optional
import datetime

# Initialize the EventManager
event_manager = EventManager()
context_manager = ContextManager()

@function_tool
def create_final_event(event: EventDetails) -> str:
    """
    Creates a new event in Google Calendar. Ensure the current date is used as a reference.
    """
    return event_manager.create_final_event(event)

@function_tool
def modify_existing_event(params: ModifyEventParams) -> str:
    """
    Modifies an existing event in Google Calendar based on a search term in the title and a time range.
    """
    return event_manager.modify_event(params)

@function_tool
def delete_event(params: DeleteEventParams) -> str:
    """
    Deletes an event in Google Calendar based on a search term in the title and a time range.
    """
    return event_manager.delete_event(params)

@function_tool
def list_events(params: EventListParams) -> str:
    """
    Lists events within a specified time range, optionally filtered by color, title, and count.
    """
    return event_manager.list_events(params)

@function_tool
def get_current_time(format: Optional[str] = None) -> str:
    """
    Returns the current date and time.

    Args:
        format: The format of the date and time in strftime style.
                Example: "%Y-%m-%d %H:%M:%S" (date and time).
    """
    return datetime.datetime.now().strftime(format) if format else str(datetime.datetime.now())

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
