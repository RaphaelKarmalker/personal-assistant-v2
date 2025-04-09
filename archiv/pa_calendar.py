from openai import OpenAI
import json

client = OpenAI()

response = client.responses.create(
    model="gpt-4o-2024-08-06",
    input=[
        {"role": "system", "content": "Extract the event information for a calendar entry."},
        {"role": "user", "content": "Set an Event for the 11th May 2025, where there is an AI course from 8pm to 9pm."}
    ],
    text={
        "format": {
            "type": "json_schema",
            "name": "calendar_event",
            "schema": {
                "type": "object",
                "properties": {
                    "start_time": {
                        "type": "string"
                    },
                    "end_time": {
                        "type": "string"
                    },
                    "name": {
                        "type": "string"
                    },
                    "description": {
                        "type": "string"
                    }
                },
                "required": ["start_time", "end_time", "name", "description"],
                "additionalProperties": False
            },
            "strict": True
        }
    }
)

event = json.loads(response.output_text)
print(event)
