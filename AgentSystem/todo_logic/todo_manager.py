from googleapiclient.errors import HttpError
from googleapiclient.discovery import build
from datetime import datetime
from typing import Optional
from tools.authentication import Authenticator
from todo_logic.models import TodoDetails, ModifyTodoParams, TaskListParams, DeleteTodoParams

class TaskManager:
    def __init__(self):
        # Authenticate and initialize the Google Tasks service
        self.service = Authenticator.authenticate("todo")

    ### Task List Methods ###
    def create_tasklist(self, title: str) -> str:
        try:
            # Create a new task list
            tasklist = {'title': title}
            result = self.service.tasklists().insert(body=tasklist).execute()
            return f"Task list '{title}' created (ID: {result['id']})"
        except HttpError as error:
            return f"Error while creating the task list: {error}"

    def delete_tasklist(self, tasklist_id: str) -> str:
        try:
            # Delete a task list by its ID
            self.service.tasklists().delete(tasklist=tasklist_id).execute()
            return f"Task list with ID '{tasklist_id}' successfully deleted."
        except HttpError as error:
            return f"Error while deleting the task list: {error}"

    def list_tasklists(self) -> str:
        try:
            # Retrieve all task lists
            results = self.service.tasklists().list().execute()
            tasklists = results.get("items", [])
            return "\n".join([f"{tasklist['title']} (ID: {tasklist['id']})" for tasklist in tasklists])
        except HttpError as error:
            return f"Error while retrieving task lists: {error}"

    ### Task Methods ###
    def create_todo(self, todo: TodoDetails) -> str:
        try:
            # Create a new task
            task = {'title': todo.title, 'status': todo.status or 'needsAction'}
            if todo.notes:
                task['notes'] = todo.notes
            if todo.due:
                task['due'] = todo.due
            result = self.service.tasks().insert(tasklist=todo.tasklist_id, body=task).execute()
            return f"Task '{todo.title}' created (ID: {result['id']})"
        except HttpError as error:
            return f"Error while creating the task: {error}"

    def delete_todo(self, params: DeleteTodoParams) -> str:
        try:
            # Delete a task by its ID
            self.service.tasks().delete(tasklist=params.tasklist_id, task=params.task_id).execute()
            return f"Task with ID '{params.task_id}' successfully deleted."
        except HttpError as error:
            return f"Error while deleting the task: {error}"

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
            return f"Task '{updated_task['title']}' successfully updated."
        except HttpError as error:
            return f"Error while updating the task: {error}"

    def list_todos(self, params: TaskListParams) -> str:
        try:
            results = self.service.tasks().list(tasklist=params.tasklist_id).execute()
            tasks = results.get("items", [])
            if not tasks:
                return "No tasks found."
            return "\n".join([f"{task['title']} (ID: {task['id']})" for task in tasks])
        except HttpError as error:
            return f"Error while retrieving tasks: {error}"
