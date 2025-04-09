import asyncio
import numpy as np
from agents import Agent, Runner
from agents.voice import (
    AudioInput,
    SingleAgentVoiceWorkflow,
    SingleAgentWorkflowCallbacks,
    VoicePipeline,
)
from util import AudioPlayer, record_audio
from agent.agent_termin import appointment_agent
from agent.agent_todo import todo_agent
from tools.context_manager import ContextManager


context_manager = ContextManager()

# Koordinator-Agent, der intern die Übergabe regelt
coordinator_agent = Agent(
    name="Coordinator Agent",
    instructions="Analyze the input and hand off to the appropriate specialized agent: To-Do or Appointment.",
    handoffs=[appointment_agent, todo_agent],
)

# Voice Pipeline konfigurieren mit dem Koordinator-Agenten
voice_pipeline = VoicePipeline(
    workflow=SingleAgentVoiceWorkflow(agent=coordinator_agent),  # Koordinator-Agent als zentraler Agent
)


# Callbacks für den Voice Agent
class WorkflowCallbacks(SingleAgentWorkflowCallbacks):
    def on_run(self, workflow: SingleAgentVoiceWorkflow, transcription: str) -> None:
        print(f"[debug] Eingabe erkannt: {transcription}")

async def run_voice_agent():
    print("Voice Agent gestartet. Du kannst jederzeit mit 'exit' beenden.")

    while True:
        try:
            # Sprachaufnahme starten
            print("Warte auf Spracheingabe...")
            #buffer = np.zeros(24000 * 3, dtype=np.int16)  # 3 Sekunden Stille als Platzhalter
            audio_input = AudioInput(buffer=record_audio())

            # Agentenausführung mit Sprachinput direkt über die Pipeline
            result = await voice_pipeline.run(audio_input)

            # Verlasse die Schleife bei 'exit'
            #transcription = result.transcript
            #if transcription.lower() in ["exit", "quit"]:
            #    print("Voice Agent beendet. Bis bald!")
             #   break

            #

            # Antwort des Agenten aus dem Pipeline-Ergebnis
            #output_text = str(result.final_output)
            #print(f"Ergebnis: {output_text}")

            with AudioPlayer() as player:
                async for event in result.stream():
                    if event.type == "voice_stream_event_audio":
                        player.add_audio(event.data)
                        print("Received audio")
                    elif event.type == "voice_stream_event_lifecycle":
                        print(f"Received lifecycle event: {event.event}")

                # Add 1 second of silence to the end of the stream to avoid cutting off the last audio.
                player.add_audio(np.zeros(24000 * 1, dtype=np.int16))

            # Kontext aktualisieren
            #Kontext hinzufügen
            context_manager.update_context("User", transcription)
            context_manager.update_context("Assistant", output_text)

        except Exception as e:
            print(f"Fehler während der Ausführung: {e}")

if __name__ == "__main__":
    asyncio.run(run_voice_agent())

    #ToDO

    #add custom workflow https://github.com/openai/openai-agents-python/blob/main/examples/voice/streamed/my_workflow.py
