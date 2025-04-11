from agents.voice import VoiceWorkflowBase, VoiceWorkflowHelper
from agents import Runner, TResponseInputItem
from collections.abc import AsyncIterator

class CustomVoiceWorkflow(VoiceWorkflowBase):
    def __init__(self, agent, context_manager):
        self.agent = agent
        self.context_manager = context_manager
        self.input_history: list[TResponseInputItem] = []

    async def run(self, transcription: str) -> AsyncIterator[str]:

        context_summary = self.context_manager.get_context_summary()
        full_input = f"History: {context_summary}\n\nNew Input: {transcription}"
        self.context_manager.update_context("User", transcription)
        print(full_input)

        result = Runner.run_streamed(self.agent, full_input)

        # 🖨️ Hier wird Text während der Sprachausgabe direkt auch in die Konsole gedruckt
        output_accumulator = ""
        async for chunk in VoiceWorkflowHelper.stream_text_from(result):
            print(chunk, end="", flush=True)  # Live-Console-Ausgabe
            output_accumulator += chunk
            yield chunk  # geht an die TTS weiter

        self.context_manager.update_context("Assistant", output_accumulator)


import asyncio
import numpy as np
from agents import Agent
from agents.voice import AudioInput, VoicePipeline
from agent.agent_termin import appointment_agent
from agent.agent_todo import todo_agent
from tools.context_manager import ContextManager
from util import record_audio, AudioPlayer
#from my_workflow import CustomVoiceWorkflow  # 👈 das ist die Klasse oben

# Kontext und Agenten definieren
context_manager = ContextManager()

coordinator_agent = Agent(
    name="Coordinator Agent",
    instructions="Analyze the input and hand off to the appropriate specialized agent: To-Do or Appointment. Rede deutsch",
    handoffs=[todo_agent, appointment_agent],
)

async def run_voice_handoff():
    print("🎙️ Voice Handoff Agent gestartet. Sag 'exit', um zu beenden.")

    # Initialisiere Workflow + Pipeline
    workflow = CustomVoiceWorkflow(agent=coordinator_agent, context_manager=context_manager)
    voice_pipeline = VoicePipeline(workflow=workflow)

    while True:
        try:
            print("🎤 Sag etwas... (drücke Leertaste zum Aufnehmen)")
            audio_input = AudioInput(buffer=record_audio())

            result = await voice_pipeline.run(audio_input)

            # Stream verarbeiten und abspielen
            with AudioPlayer() as player:
                async for event in result.stream():
                    if event.type == "voice_stream_event_audio":
                        player.add_audio(event.data)
                    elif event.type == "voice_stream_event_lifecycle":
                        print(f"[Lifecycle] {event.event}")

                # 1 Sekunde Stille anhängen
                player.add_audio(np.zeros(24000 * 1, dtype=np.int16))

        except Exception as e:
            print(f"❌ Fehler während der Ausführung: {e}")

# Starte die App
if __name__ == "__main__":
    asyncio.run(run_voice_handoff())

