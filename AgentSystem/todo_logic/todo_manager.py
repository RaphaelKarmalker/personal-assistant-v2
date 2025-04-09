from googleapiclient.errors import HttpError
from googleapiclient.discovery import build
from datetime import datetime
from typing import Optional
from tools.authentication import Authenticator
from todo_logic.models import TodoDetails, ModifyTodoParams, TaskListParams, DeleteTodoParams

class TaskManager:
    def __init__(self):
        self.service = Authenticator.authenticate("todo")

    ### 🗂️ Aufgabenlisten-Methoden ###
    def create_tasklist(self, title: str) -> str:
        try:
            tasklist = {'title': title}
            result = self.service.tasklists().insert(body=tasklist).execute()
            return f"Aufgabenliste '{title}' erstellt (ID: {result['id']})"
        except HttpError as error:
            return f"Fehler beim Erstellen der Aufgabenliste: {error}"

    def delete_tasklist(self, tasklist_id: str) -> str:
        try:
            self.service.tasklists().delete(tasklist=tasklist_id).execute()
            return f"Aufgabenliste mit ID '{tasklist_id}' erfolgreich gelöscht."
        except HttpError as error:
            return f"Fehler beim Löschen der Aufgabenliste: {error}"

    def list_tasklists(self) -> str:
        try:
            results = self.service.tasklists().list().execute()
            tasklists = results.get("items", [])
            return "\n".join([f"{tasklist['title']} (ID: {tasklist['id']})" for tasklist in tasklists])
        except HttpError as error:
            return f"Fehler beim Abrufen der Aufgabenlisten: {error}"

    ### ✅ Aufgaben-Methoden ###
    def create_todo(self, todo: TodoDetails) -> str:
        try:
            task = {'title': todo.title, 'status': todo.status or 'needsAction'}
            if todo.notes:
                task['notes'] = todo.notes
            if todo.due:
                task['due'] = todo.due
            result = self.service.tasks().insert(tasklist=todo.tasklist_id, body=task).execute()
            return f"Aufgabe '{todo.title}' erstellt (ID: {result['id']})"
        except HttpError as error:
            return f"Fehler beim Erstellen der Aufgabe: {error}"

    def delete_todo(self, params: DeleteTodoParams) -> str:
        try:
            self.service.tasks().delete(tasklist=params.tasklist_id, task=params.task_id).execute()
            return f"Aufgabe mit ID '{params.task_id}' erfolgreich gelöscht."
        except HttpError as error:
            return f"Fehler beim Löschen der Aufgabe: {error}"

    def modify_todo(self, params: ModifyTodoParams) -> str:
        try:
            task = self.service.tasks().get(tasklist=params.tasklist_id, task=params.task_id).execute()
            if params.new_title:
                task['title'] = params.new_title
            if params.new_notes:
                task['notes'] = params.new_notes
            if params.new_due:
                task['due'] = params.new_due
            if params.new_status:
                task['status'] = params.new_status
            updated_task = self.service.tasks().update(tasklist=params.tasklist_id, task=params.task_id, body=task).execute()
            return f"Aufgabe '{updated_task['title']}' erfolgreich aktualisiert."
        except HttpError as error:
            return f"Fehler beim Ändern der Aufgabe: {error}"

    def list_todos(self, params: TaskListParams) -> str:
        try:
            results = self.service.tasks().list(tasklist=params.tasklist_id).execute()
            tasks = results.get("items", [])
            if not tasks:
                return "Keine Aufgaben gefunden."
            return "\n".join([f"{task['title']} (ID: {task['id']})" for task in tasks])
        except HttpError as error:
            return f"Fehler beim Abrufen der Aufgaben: {error}"
