from agents import Agent, Runner
from pydantic import BaseModel
import asyncio

# Pydantic-Modelle für strukturierte Ausgaben
class ToDo(BaseModel):
    title: str
    deadline: str
    time: str

class Reminder(BaseModel):
    reminder_text: str
    date: str
    time: str

# Specialized Agents

# To-Do Agent
todo_agent = Agent(
    name="To-Do Agent",
    instructions="Erstelle eine strukturierte To-Do-Eintragung. Nutze die vorliegenden Informationen, ohne Ergänzungen vorzunehmen.",
    output_type=ToDo,
    model="gpt-4o"
)

# Reminder Agent
reminder_agent = Agent(
    name="Reminder Agent",
    instructions="Setze eine strukturierte Erinnerung basierend auf den vorliegenden Informationen. Ergänze keine fehlenden Daten.",
    output_type=Reminder,
    model="gpt-4o"
)

# Dynamic Assistant Agent: Fragt bei unvollständiger Eingabe nach
assistant_agent = Agent(
    name="Assistant Agent",
    instructions="""
        Wenn die Eingabe unvollständig ist (z.B. keine Uhrzeit oder kein Datum), stelle gezielte Rückfragen.
        Beispiel: 'Soll ich eine Uhrzeit hinzufügen? Vielleicht heute um 18 Uhr?'
        Warte auf die Bestätigung des Nutzers und ergänze die Eingabe entsprechend.
        Antworte niemals eigenständig mit einer Uhrzeit ohne Rückfrage.
    """,
    model="gpt-4o"
)

# Manager Agent: Entscheidet, ob Assistant Agent benötigt wird
manager_agent = Agent(
    name="Manager Agent",
    instructions="""
        Deine Aufgabe ist es nur festzustellen, ob die Eingabe vollständig oder unvollständig ist.
        Antworte niemals selbst mit einer Ergänzung oder Vervollständigung.
        Wenn die Eingabe unvollständig ist (z.B. fehlende Uhrzeit), leite sie ohne Änderungen an den Assistant Agent weiter.
        Gib keine eigene Interpretation oder Vermutung ab.
    """,
    handoffs=[assistant_agent, todo_agent, reminder_agent],
    model="gpt-4o"
)

# Hauptfunktion zur Ausführung
async def run_agent(user_input):
    try:
        # Step 1: Manager Agent entscheidet
        response = await Runner.run(manager_agent, input=user_input)
        print("Manager Agent Response:")
        print(response.final_output)

        # Check if clarification is needed
        if "incomplete" in response.final_output or "missing" in response.final_output:
            print("\nAssistant Agent wird zur Klärung hinzugezogen.")
            clarification = await Runner.run(assistant_agent, input=user_input)
            print("Assistant Agent Rückfrage:")
            print(clarification.final_output)

            # User input after the Assistant Agent's question
            user_reply = input("Antwort: ")
            updated_input = f"{user_input} {user_reply}"
            
            # Final step: Manager Agent verarbeitet die aktualisierte Eingabe
            final_response = await Runner.run(manager_agent, input=updated_input)
            print("\nFinal Response:")
            print(final_response.final_output)
        else:
            print("\nDirekte Antwort vom Manager Agent:")
            print(response.final_output)

    except Exception as e:
        print(f"Fehler während der Agentenausführung: {e}")

# Nutzerinteraktion
user_input = input("Was möchtest du tun? (z.B. To-Do oder Erinnerung): ")

# Asynchrone Ausführung
asyncio.run(run_agent(user_input))
