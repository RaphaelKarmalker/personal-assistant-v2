from pydantic import BaseModel, Field
from typing import List, Optional

# 📝 Modell für eine To-Do-Aufgabe
class TodoDetails(BaseModel):
    title: str = Field(..., description="Titel der Aufgabe")
    notes: Optional[str] = Field(None, description="Zusätzliche Notizen zur Aufgabe")
    due: Optional[str] = Field(None, description="Fälligkeitsdatum im ISO-Format (z.B. '2025-04-10T17:00:00.000Z')")
    status: str = Field(..., description="Status der Aufgabe ('needsAction' oder 'completed')")
    tasklist_id: str = Field(..., description="ID der Aufgabenliste")

# 🔄 Modell für die Modifikation einer Aufgabe
class ModifyTodoParams(BaseModel):
    tasklist_id: str = Field(..., description="ID der Aufgabenliste")
    task_id: str = Field(..., description="ID der Aufgabe")
    new_title: Optional[str] = Field(None, description="Neuer Titel der Aufgabe")
    new_notes: Optional[str] = Field(None, description="Neue Notizen zur Aufgabe")
    new_due: Optional[str] = Field(None, description="Neues Fälligkeitsdatum im ISO-Format")
    new_status: Optional[str] = Field(None, description="Neuer Status der Aufgabe ('needsAction' oder 'completed')")

# 📋 Modell zum Auflisten von Aufgaben
class TaskListParams(BaseModel):
    tasklist_id: str = Field(..., description="ID der Aufgabenliste")
    max_results: Optional[int] = Field(None, description="Maximale Anzahl anzuzeigender Aufgaben")

# ❌ Modell zum Löschen einer Aufgabe
class DeleteTodoParams(BaseModel):
    tasklist_id: str = Field(..., description="ID der Aufgabenliste")
    task_id: str = Field(..., description="ID der Aufgabe")
