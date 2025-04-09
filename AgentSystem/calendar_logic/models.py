# 📅 Model für Erinnerungen
from pydantic import BaseModel, Field
from typing import List, Optional

# 📅 Model für Ereignis-Löschparameter
class DeleteEventParams(BaseModel):
    search_name: str = Field(..., description="Teil des Titels des zu löschenden Ereignisses")
    start_time: str = Field(..., description="Startzeit des Suchzeitraums im ISO-Format")
    end_time: str = Field(..., description="Endzeit des Suchzeitraums im ISO-Format")


class ReminderModel(BaseModel):
    method: str = Field(..., description="Methode der Erinnerung (email, popup)")
    minutes: int = Field(..., description="Anzahl Minuten vor dem Ereignis")

# 📅 Model für Ereignis-Modifikationsparameter
class ModifyEventParams(BaseModel):
    search_name: str = Field(..., description="Teil des Titels des zu ändernden Ereignisses")
    start_time: str = Field(..., description="Startzeit des Suchzeitraums im ISO-Format")
    end_time: str = Field(..., description="Endzeit des Suchzeitraums im ISO-Format")
    new_summary: Optional[str] = Field(None, description="Neuer Titel des Ereignisses")
    new_start_time: Optional[str] = Field(None, description="Neue Startzeit im ISO-Format")
    new_end_time: Optional[str] = Field(None, description="Neue Endzeit im ISO-Format")
    new_description: Optional[str] = Field(None, description="Neue Beschreibung des Ereignisses")
    new_location: Optional[str] = Field(None, description="Neuer Veranstaltungsort")
    new_attendees: Optional[List[str]] = Field(None, description="Liste neuer E-Mail-Adressen der Teilnehmer")
    new_reminders: Optional[List[ReminderModel]] = Field(None, description="Liste neuer Erinnerungen")
    new_recurrence: Optional[List[str]] = Field(None, description="Neue Wiederholung des Ereignisses")
    new_color_id: Optional[int] = Field(None, description="Neue Farb-ID zur Kategorisierung")


# 📅 Model für Ereignis-Details
class EventDetails(BaseModel):
    summary: str = Field(..., description="Titel des Ereignisses")
    start_time: str = Field(..., description="Startzeit im ISO-Format (z.B. '2025-04-07T10:00:00')")
    end_time: str = Field(..., description="Endzeit im ISO-Format (z.B. '2025-04-07T11:00:00')")
    description: Optional[str] = Field(None, description="Beschreibung des Ereignisses")
    location: Optional[str] = Field(None, description="Veranstaltungsort")
    attendees: Optional[List[str]] = Field(None, description="Liste von E-Mail-Adressen der Teilnehmer")
    reminders: Optional[List[ReminderModel]] = Field(None, description="Liste von Erinnerungen")
    recurrence: Optional[List[str]] = Field(None, description="Wiederholung des Ereignisses")
    color_id: Optional[int] = Field(None, description="Farb-ID zur Kategorisierung")

# 📅 Model für Ereignis-Liste-Parameter
class EventListParams(BaseModel):
    start_time: str = Field(..., description="Startzeit des Zeitraums im ISO-Format")
    end_time: str = Field(..., description="Endzeit des Zeitraums im ISO-Format")
    max_results: Optional[int] = Field(None, description="Maximale Anzahl der anzuzeigenden Ereignisse")
    color_id: Optional[int] = Field(None, description="Farb-ID zum Filtern der Ereignisse")
    title: Optional[str] = Field(None, description="Stichwort im Titel zum Filtern")

