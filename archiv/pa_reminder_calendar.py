from openai import OpenAI
import json

client = OpenAI()

def decide_event_type(user_input):
    """ Das Modell entscheidet aktiv, ob es sich um eine Erinnerung oder ein Kalendereintrag handelt. """
    response = client.responses.create(
        model="gpt-4o-2024-08-06",
        input=[
            {"role": "system", "content": "Decide whether the following input is a calendar event or a reminder."},
            {"role": "user", "content": user_input}
        ],
        text={
            "format": {
                "type": "json_schema",
                "name": "event_decision",
                "schema": {
                    "type": "object",
                    "properties": {
                        "event_type": {
                            "type": "string",
                            "enum": ["calendar", "reminder"]
                        }
                    },
                    "required": ["event_type"],
                    "additionalProperties": False
                },
                "strict": True
            }
        }
    )
    decision = json.loads(response.output_text)
    return decision.get("event_type")

def get_event_response(user_input, event_type):
    """ Holt die strukturierten Daten basierend auf dem Event-Typ """
    if event_type == "calendar":
        schema = {
            "type": "object",
            "properties": {
                "event_name": {"type": "string"},
                "date": {"type": "string"},
                "time": {"type": "string"},
                "participants": {
                    "type": "array",
                    "items": {"type": "string"}
                }
            },
            "required": ["event_name", "date", "time", "participants"],
            "additionalProperties": False
        }
    elif event_type == "reminder":
        schema = {
            "type": "object",
            "properties": {
                "reminder_text": {"type": "string"},
                "reminder_date": {"type": "string"},
                "reminder_time": {"type": "string"}
            },
            "required": ["reminder_text", "reminder_date", "reminder_time"],
            "additionalProperties": False
        }

    response = client.responses.create(
        model="gpt-4o-2024-08-06",
        input=[
            {"role": "system", "content": f"Extract the {event_type} information."},
            {"role": "user", "content": user_input}
        ],
        text={
            "format": {
                "type": "json_schema",
                "name": f"{event_type}_event",
                "schema": schema,
                "strict": True
            }
        }
    )
    return json.loads(response.output_text)

# Eingabe vom Benutzer
user_input = input("Gib deine Anfrage ein: ")

# Modell entscheidet aktiv, ob Kalender oder Erinnerung
event_type = decide_event_type(user_input)

if event_type:
    # Holen des strukturierten Outputs
    try:
        event = get_event_response(user_input, event_type)
        print(f"Erkannter Typ: {event_type.capitalize()}")
        print(json.dumps(event, indent=4))
    except Exception as e:
        print(f"Fehler bei der Verarbeitung: {e}")
else:
    print("Fehler: Das Modell konnte den Event-Typ nicht bestimmen.")
