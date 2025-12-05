import asyncio
import time
from datetime import timedelta
from agent.agent_termin import appointment_agent
from agent.agent_todo import todo_agent
from tools.context_manager import ContextManager
from tools.stt_tts import Converter
from agents import Agent, Runner, WebSearchTool
import re
from typing import Union
import os


class HandoffAgentSystem:
    def __init__(self, debug_time: bool = False):
        # Initialize context manager and text-to-speech converter
        self.context_manager = ContextManager()
        self.converter = Converter()
        self.timestamps = {}
        self.debug_time = debug_time

        # Define the coordinator agent with specific instructions and tools
        self.coordinator_agent = Agent(
            name="Coordinator Agent",
            instructions=(
                "Try to keep responses concise."
            ),
            handoffs=[todo_agent, appointment_agent],
            tools=[WebSearchTool()]
        )

    async def run(self, audio_input: Union[str, bytes]):
        # Record the start timestamp
        self.timestamps["start"] = time.time()
        audio_input, temp_path = self.prepare_audio_input(audio_input)
        try:
            # Convert speech to text
            user_input = self.speech_to_text(audio_input)

            # Exit condition for the agent
            if user_input.lower() in ["exit", "quit"]:
                print("Handoff Agent terminated. Goodbye!")
                return

            # Process the user input and generate a response
            response = await self.run_assistant(user_input)
            print(f"Result: {response}")

            # Clean the response for text-to-speech conversion
            cleaned_response = self.clean_for_tts(response)
            audio_response = self.text_to_speech(cleaned_response)

            # Update the context with the new user input and response
            self.update_context(user_input, response)
            self.timestamps["end"] = time.time()

            # Print debug information if enabled
            if self.debug_time:
                self.print_debug_times()
            if temp_path and os.path.exists(temp_path):
                os.remove(temp_path)
            return audio_response

        except Exception as e:
            print(f"Error during agent execution: {e}")
            return None

    def speech_to_text(self, audio_input):
        # Convert speech input to text
        self.timestamps["stt_start"] = time.time()
        user_input = str(self.converter.speech_to_text(audio_input)) #AUDIO
        self.timestamps["stt_end"] = time.time()
        return user_input
    
    def text_to_speech(self, cleaned_response):
        # Convert text response to speech
        self.timestamps["tts_start"] = time.time()
        audio_response = self.converter.text_to_speech(cleaned_response)
        self.timestamps["tts_end"] = time.time()
        return audio_response

    async def run_assistant(self, user_input):
        # Run the assistant agent with the given user input
        context_summary = self.context_manager.get_context_summary()
        full_input = f"History: {context_summary}\n\nNew Input: {user_input}"

        self.timestamps["agent_start"] = time.time()
        result = await Runner.run(self.coordinator_agent, full_input)
        self.timestamps["agent_end"] = time.time()
        return result.final_output

    def update_context(self, user_input, assistant_response):
        # Update the context manager with new user input and assistant response
        self.context_manager.update_context("User", user_input)
        self.context_manager.update_context("Assistant", assistant_response)

    def print_debug_times(self):
        # Print the timing information for debugging
        print("\n⏱️ Timing Overview:")
        def duration(label, start, end):
            return f"{label:<20} → {timedelta(seconds=self.timestamps[end] - self.timestamps[start])}"

        print(duration("Speech-to-Text", "stt_start", "stt_end"))
        print(duration("Agent Run", "agent_start", "agent_end"))
        print(duration("Text-to-Speech", "tts_start", "tts_end"))

        total_time = self.timestamps["end"] - self.timestamps["start"]
        print(f"\n🕒 Total Duration: {timedelta(seconds=total_time)}")
    

    def clean_for_tts(self, text):
        # Replace any complete sentence containing an https link with "Task completed!"
        text = re.sub(r"[^.!?]*https?://[^\s\)]+[^.!?]*[.!?]", " Task completed!", text)

        # Remove Markdown, bullet points, parentheses, etc.
        text = re.sub(r"\*\*|__|\*", "", text)                    # Markdown bold
        text = re.sub(r"\n\s*[-•]\s*", " ", text)                 # List items
        text = re.sub(r"\([^)]*\)", "", text)                     # Content in parentheses
        text = re.sub(r"\s+", " ", text)                          # Multiple spaces
        return text.strip()

    def prepare_audio_input(self, audio_input: Union[str, bytes]) -> tuple[str, Union[str, None]]:
        """
        Convert bytes to a temporary file and return the path.
        Also returns the temporary path for potential deletion.
        """
        if isinstance(audio_input, bytes):
            temp_path = "temp_input.wav"
            with open(temp_path, "wb") as f:
                f.write(audio_input)
            return temp_path, temp_path
        else:
            return audio_input, None



# Start the asynchronous loop
if __name__ == "__main__":
    agent_system = HandoffAgentSystem(debug_time=True)
    asyncio.run(agent_system.run("test_audio.wav"))
