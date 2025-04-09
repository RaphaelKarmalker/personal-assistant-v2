### agent/agent_runner.py
from agents import Agent, function_tool, Runner
from todo_logic.todo_manager import TaskManager
from todo_logic.models import TodoDetails, ModifyTodoParams, TaskListParams, DeleteTodoParams
from tools.context_manager import ContextManager
from typing import Optional
import datetime

# Initialisiere den TaskManager
task_manager = TaskManager()
context_manager = ContextManager()

@function_tool
def create_todo(todo: TodoDetails) -> str:
    """
    Erstellt eine neue To-Do-Aufgabe.
    """
    return task_manager.create_todo(todo)

@function_tool
def modify_todo(params: ModifyTodoParams) -> str:
    """
    Modifiziert eine bestehende To-Do-Aufgabe.
    """
    return task_manager.modify_todo(params)

@function_tool
def delete_todo(params: DeleteTodoParams) -> str:
    """
    Löscht eine To-Do-Aufgabe.
    """
    return task_manager.delete_todo(params)

@function_tool
def list_todos(params: TaskListParams) -> str:
    """
    Listet alle Aufgaben in einer bestimmten Aufgabenliste auf.
    """
    return task_manager.list_todos(params)

@function_tool
def create_tasklist(title: str) -> str:
    """
    Erstellt eine neue Aufgabenliste.
    """
    return task_manager.create_tasklist(title)

@function_tool
def delete_tasklist(tasklist_id: str) -> str:
    """
    Löscht eine Aufgabenliste.
    """
    return task_manager.delete_tasklist(tasklist_id)

@function_tool
def list_tasklists() -> str:
    """
    Listet alle vorhandenen Aufgabenlisten auf.
    """
    return task_manager.list_tasklists()

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
        if format is None or format.strip() == "":
            format = "%Y-%m-%d %H:%M:%S"
        current_date = datetime.datetime.now().strftime(format)
        return current_date
    except Exception as e:
        return f"Fehler beim Formatieren der Uhrzeit: {str(e)}"

todo_agent = Agent(
    name="ToDo Agent",
    handoff_description="Agent for handling toDo.",
    instructions="Agent zur Erstellung, Auflistung, Änderung und Löschung von ToDos und Aufgabenlisten. Achte auf die Verwendung des aktuellen Datums bei Aufgaben.",
    tools=[create_todo, modify_todo, delete_todo, list_todos, create_tasklist, delete_tasklist, list_tasklists, get_current_time],
    model="gpt-4o"
)

async def run_agent_todo():
    print("ToDo Agent gestartet. Du kannst jederzeit mit 'exit' beenden.")
    while True:
        user_input = input("Du: ")
        if user_input.lower() in ["exit", "quit"]:
            print("Agent beendet. Bis bald!")
            break

        try:
            context_summary = context_manager.get_context_summary()
            full_input = f"History: {context_summary}\n\nNew Input: {user_input}"

            result = await Runner.run(todo_agent, full_input)
            output = str(result.final_output)
            print(f"Ergebnis: {output}")

            context_manager.update_context("User", user_input)
            context_manager.update_context("Assistant", output)

        except Exception as e:
            print(f"Fehler: {e}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(run_agent_todo())