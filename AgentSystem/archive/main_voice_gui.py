from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING
import numpy as np
import sounddevice as sd
from textual import events
from textual.app import App, ComposeResult
from textual.containers import Container
from textual.reactive import reactive
from textual.widgets import RichLog, Static
from typing_extensions import override

from agents.voice import StreamedAudioInput, VoicePipeline
from agents.voice import VoiceWorkflowBase, VoiceWorkflowHelper
from agents import Runner, TResponseInputItem
from collections.abc import AsyncIterator

# 🧠 Custom Workflow mit Kontext-Handling & Debug-Ausgaben
class CustomVoiceWorkflow(VoiceWorkflowBase):
    def __init__(self, agent, context_manager):
        self.agent = agent
        self.context_manager = context_manager
        self.input_history: list[TResponseInputItem] = []

    async def run(self, transcription: str) -> AsyncIterator[str]:
        print(f"\n🎙️ Transkription: {transcription}")
        self.context_manager.update_context("User", transcription)

        context_summary = self.context_manager.get_context_summary()
        full_input = f"History: {context_summary}\n\nNew Input: {transcription}"
        self.input_history.append({"role": "user", "content": full_input})

        result = Runner.run_streamed(self.agent, self.input_history)

        output_accumulator = ""
        print("🔁 Streaming Antwort vom Agenten...")
        async for chunk in VoiceWorkflowHelper.stream_text_from(result):
            print(chunk, end="", flush=True)  # Zeige live-Ausgabe
            output_accumulator += chunk
            yield chunk

        if not output_accumulator:
            print("❌ Kein Output vom Agenten erhalten.")
        else:
            print(f"\n✅ Finaler Output: {output_accumulator}")

        self.context_manager.update_context("Assistant", output_accumulator)
        self.input_history = result.to_input_list()

# 🔧 Einstellungen
CHUNK_LENGTH_S = 0.05
SAMPLE_RATE = 24000
FORMAT = np.int16
CHANNELS = 1

class Header(Static):
    session_id = reactive("")
    @override
    def render(self) -> str:
        return "Sprich mit dem Agenten. Aufnahme mit K starten/stoppen."

class AudioStatusIndicator(Static):
    is_recording = reactive(False)
    @override
    def render(self) -> str:
        return (
            "🔴 Aufnahme läuft... (K = Stop)" if self.is_recording
            else "⚪ Drücke K zum Aufnehmen (Q zum Beenden)"
        )

class VoiceApp(App[None]):
    CSS = """
        Screen { background: #1a1b26; }
        Container { border: double rgb(91, 164, 91); }
        #bottom-pane { height: 90%; border: round rgb(205, 133, 63); }
        #status-indicator, #session-display { height: 3; background: #2a2b36; border: solid rgb(91, 164, 91); margin: 1 1; }
        Static { color: white; }
    """

    def __init__(self) -> None:
        super().__init__()
        self.should_send_audio = asyncio.Event()
        self._audio_input = StreamedAudioInput()

        # Agent & Kontextmanager
        from tools.context_manager import ContextManager
        from agent.agent_termin import appointment_agent
        from agent.agent_todo import todo_agent
        from agents import Agent

        context_manager = ContextManager()
        coordinator_agent = Agent(
            name="Coordinator Agent",
            instructions="Analyze the input and hand off to the appropriate specialized agent: To-Do or Appointment.",
            handoffs=[todo_agent, appointment_agent],
        )

        # Workflow & VoicePipeline
        workflow = CustomVoiceWorkflow(agent=coordinator_agent, context_manager=context_manager)
        self.pipeline = VoicePipeline(workflow=workflow)

        self.audio_player = sd.OutputStream(
            samplerate=SAMPLE_RATE,
            channels=CHANNELS,
            dtype=FORMAT,
        )

    @override
    def compose(self) -> ComposeResult:
        with Container():
            yield Header(id="session-display")
            yield AudioStatusIndicator(id="status-indicator")
            yield RichLog(id="bottom-pane", wrap=True, highlight=True, markup=True)

    async def on_mount(self) -> None:
        self.run_worker(self.start_voice_pipeline())
        self.run_worker(self.send_mic_audio())

    async def start_voice_pipeline(self) -> None:
        self.audio_player.start()
        log = self.query_one("#bottom-pane", RichLog)
        try:
            result = await self.pipeline.run(self._audio_input)

            transcribed_output = ""

            async for event in result.stream():
                if event.type == "voice_stream_event_audio":
                    self.audio_player.write(event.data)
                    log.write(f"[Audio] {len(event.data) if event.data is not None else '0'} bytes")
                elif event.type == "voice_stream_event_lifecycle":
                    log.write(f"[Lifecycle] {event.event}")
                elif event.type == "voice_stream_event_text":
                    transcribed_output += event.data
                    log.write(f"[Antwort] {event.data}")  # Live-Textanzeige

            if transcribed_output:
                log.write(f"[🔊 Gesprochen] {transcribed_output}")

        except Exception as e:
            log = self.query_one("#bottom-pane", RichLog)
            log.write(f"[Fehler] {e}")
        finally:
            self.audio_player.close()

    async def send_mic_audio(self) -> None:
        read_size = int(SAMPLE_RATE * 0.02)
        stream = sd.InputStream(
            channels=CHANNELS,
            samplerate=SAMPLE_RATE,
            dtype=FORMAT,
        )
        stream.start()

        status = self.query_one(AudioStatusIndicator)
        try:
            while True:
                if stream.read_available < read_size:
                    await asyncio.sleep(0)
                    continue

                await self.should_send_audio.wait()
                status.is_recording = True

                data, _ = stream.read(read_size)
                await self._audio_input.add_audio(data)
                await asyncio.sleep(0)
        finally:
            stream.stop()
            stream.close()

    async def on_key(self, event: events.Key) -> None:
        if event.key == "q":
            self.exit()
        elif event.key == "k":
            status = self.query_one(AudioStatusIndicator)
            if status.is_recording:
                self.should_send_audio.clear()
                status.is_recording = False
            else:
                self.should_send_audio.set()
                status.is_recording = True

if __name__ == "__main__":
    VoiceApp().run()
