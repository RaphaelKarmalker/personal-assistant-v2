### main.py
import asyncio
from agent.agent_termin import appointment_agent
from agent.agent_todo import todo_agent
from tools.context_manager import ContextManager
from agents import Agent, Runner

context_manager = ContextManager()

coordinator_agent = Agent(
    name="Coordinator Agent",
    instructions=(
        "Analyze the input and hand off to the appropriate specialized agent: To-Do, or Appointment. "
        "Always consider the previous context when processing the current input. "
        #"If the user provides additional details or modifies a previous task, combine it with the last context."
    ),
    handoffs=[todo_agent, appointment_agent],
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

        try:
            # Kontext zusammenfassen und der Eingabe voranstellen
            context_summary = context_manager.get_context_summary()
            full_input = f"History: {context_summary}\n\nNew Input: {user_input}"

            # Läuft den Agenten mit der kombinierten Eingabe
            result = await Runner.run(coordinator_agent, full_input)
            print(f"Ergebnis: {result.final_output}")

            context_manager.update_context("User", user_input)
            context_manager.update_context("Assistant", result.final_output)

        except Exception as e:
            print(f"Fehler während der Agentenausführung: {e}")

# Starte die asynchrone Schleife
if __name__ == "__main__":
    asyncio.run(run_handoff())