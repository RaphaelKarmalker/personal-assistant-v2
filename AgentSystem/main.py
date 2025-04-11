import asyncio
import time
from datetime import timedelta
from agent.agent_termin import appointment_agent
from agent.agent_todo import todo_agent
from tools.context_manager import ContextManager
from tools.stt_tts import Converter
from agents import Agent, Runner, WebSearchTool
import re

class HandoffAgentSystem:
    def __init__(self, debug_time: bool = False):
        self.context_manager = ContextManager()
        self.converter = Converter()
        self.timestamps = {}
        self.debug_time = debug_time

        self.coordinator_agent = Agent(
            name="Coordinator Agent",
            instructions=(
                #"if neccesarry hand off to the appropriate specialized agent: To-Do, or Appointment. "
                #"Always consider the previous context when processing the current input. "
                "Versuch die Antworten kurz zu halten."
                #"Respond in a form that can be naturally read aloud by a voice assistant." 
                #"Do not use bullet points, headings, or formatting. If retrieving data via web search, summarize the key points in a conversational, natural tone without copying list structures."

            ),
            handoffs=[todo_agent, appointment_agent],
            tools=[WebSearchTool()]
        )

    async def run(self):
        print("Handoff Agent gestartet. Du kannst jederzeit mit 'exit' beenden.")
        self.timestamps["start"] = time.time()

        try:
            #user_input = self.speech_to_text()
            user_input = input("")

            if user_input.lower() in ["exit", "quit"]:
                print("Handoff Agent beendet. Bis bald!")
                return
            
            response = await self.runAsisstant(user_input)
            print(f"Ergebnis: {response}")

            cleaned_response = self.clean_for_tts(response)
            self.text_to_speech(cleaned_response)

            self.update_context(user_input, response)
            self.timestamps["end"] = time.time()

            if self.debug_time:
                self.print_debug_times()

        except Exception as e:
            print(f"Fehler während der Agentenausführung: {e}")

    def speech_to_text(self):
        self.timestamps["stt_start"] = time.time()
        user_input = str(self.converter.speech_to_text("test_audio.wav")) #AUDIO
        self.timestamps["stt_end"] = time.time()
        return user_input
    
    def text_to_speech(self, cleaned_response):
        self.timestamps["tts_start"] = time.time()
        self.converter.text_to_speech(cleaned_response)
        self.timestamps["tts_end"] = time.time()

    async def runAsisstant(self, user_input):
        context_summary = self.context_manager.get_context_summary()
        full_input = f"History: {context_summary}\n\nNew Input: {user_input}"

        self.timestamps["agent_start"] = time.time()
        result = await Runner.run(self.coordinator_agent, full_input)
        self.timestamps["agent_end"] = time.time()
        return result.final_output

    def update_context(self, user_input, assistant_response):
        self.context_manager.update_context("User", user_input)
        self.context_manager.update_context("Assistant", assistant_response)

    def print_debug_times(self):
        print("\n⏱️ Zeitübersicht:")
        def duration(label, start, end):
            return f"{label:<20} → {timedelta(seconds=self.timestamps[end] - self.timestamps[start])}"

        #print(duration("Speech-to-Text", "stt_start", "stt_end"))
        print(duration("Agentenlauf", "agent_start", "agent_end"))
        print(duration("Text-to-Speech", "tts_start", "tts_end"))

        total_time = self.timestamps["end"] - self.timestamps["start"]
        print(f"\n🕒 Gesamtdauer: {timedelta(seconds=total_time)}")
    
    
    def clean_for_tts(self, text):
        # Entferne Markdown, Bulletpoints, Links
        text = re.sub(r"\*\*|__|\*", "", text)                 # Markdown-Fett
        text = re.sub(r"\n\s*[-•]\s*", " ", text)              # Listenpunkte
        text = re.sub(r"https?://\S+", "", text)               # Links
        text = re.sub(r"\([^)]*\)", "", text)                  # Inhalte in Klammern (Quellen)
        text = re.sub(r"\s+", " ", text)                       # Mehrfache Leerzeichen
        return text.strip()


# Starte die asynchrone Schleife
if __name__ == "__main__":
    agent_system = HandoffAgentSystem(debug_time=True)
    asyncio.run(agent_system.run())
