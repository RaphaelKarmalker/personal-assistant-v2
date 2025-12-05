from pydantic import BaseModel, Field
from typing import List, Optional

# Model for event deletion parameters
class DeleteEventParams(BaseModel):
    search_name: str = Field(..., description="Part of the title of the event to be deleted")
    start_time: str = Field(..., description="Start time of the search range in ISO format")
    end_time: str = Field(..., description="End time of the search range in ISO format")


# Model for reminders
class ReminderModel(BaseModel):
    method: str = Field(..., description="Reminder method (email, popup)")
    minutes: int = Field(..., description="Number of minutes before the event")

# Model for event modification parameters
class ModifyEventParams(BaseModel):
    search_name: str = Field(..., description="Part of the title of the event to be modified")
    start_time: str = Field(..., description="Start time of the search range in ISO format")
    end_time: str = Field(..., description="End time of the search range in ISO format")
    new_summary: Optional[str] = Field(None, description="New title of the event")
    new_start_time: Optional[str] = Field(None, description="New start time in ISO format")
    new_end_time: Optional[str] = Field(None, description="New end time in ISO format")
    new_description: Optional[str] = Field(None, description="New description of the event")
    new_location: Optional[str] = Field(None, description="New location of the event")
    new_attendees: Optional[List[str]] = Field(None, description="List of new attendee email addresses")
    new_reminders: Optional[List[ReminderModel]] = Field(None, description="List of new reminders")
    new_recurrence: Optional[List[str]] = Field(None, description="New recurrence pattern for the event")
    new_color_id: Optional[int] = Field(None, description="New color ID for categorization")


# Model for event details
class EventDetails(BaseModel):
    summary: str = Field(..., description="Title of the event")
    start_time: str = Field(..., description="Start time in ISO format (e.g., '2025-04-07T10:00:00')")
    end_time: str = Field(..., description="End time in ISO format (e.g., '2025-04-07T11:00:00')")
    description: Optional[str] = Field(None, description="Description of the event")
    location: Optional[str] = Field(None, description="Location of the event")
    attendees: Optional[List[str]] = Field(None, description="List of attendee email addresses")
    reminders: Optional[List[ReminderModel]] = Field(None, description="List of reminders")
    recurrence: Optional[List[str]] = Field(None, description="Recurrence pattern for the event")
    color_id: Optional[int] = Field(None, description="Color ID for categorization")

# Model for event listing parameters
class EventListParams(BaseModel):
    start_time: str = Field(..., description="Start time of the range in ISO format")
    end_time: str = Field(..., description="End time of the range in ISO format")
    max_results: Optional[int] = Field(None, description="Maximum number of events to display")
    color_id: Optional[int] = Field(None, description="Color ID to filter events")
    title: Optional[str] = Field(None, description="Keyword in the title to filter events")

