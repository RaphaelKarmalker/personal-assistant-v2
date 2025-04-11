from tools.authentication import Authenticator
from google.cloud import texttospeech, speech
import io
import os

class Converter:
    def __init__(self):
        self.tts_client = Authenticator.authenticate("tts")
        self.stt_client = Authenticator.authenticate("stt")

        if not self.tts_client:
            print("⚠️ TTS-Authentifizierung fehlgeschlagen.")
        if not self.stt_client:
            print("⚠️ STT-Authentifizierung fehlgeschlagen.")

    def text_to_speech(self, text: str, output_file: str = "output.mp3", voice_name="de-DE-Chirp3-HD-Leda"): # Alternative de-DE-Wavenet-H for faster
        if not self.tts_client:
            return

        synthesis_input = texttospeech.SynthesisInput(text=text)

        voice = texttospeech.VoiceSelectionParams(
            language_code="de-DE",
            name=voice_name,
            #ssml_gender=texttospeech.SsmlVoiceGender.MALE
        )

        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3
        )

        try:
            response = self.tts_client.synthesize_speech(
                input=synthesis_input,
                voice=voice,
                audio_config=audio_config
            )

            with open(output_file, "wb") as out:
                out.write(response.audio_content)
                print(f"✅ TTS: Audio gespeichert als: {output_file}")
        except Exception as e:
            print("❌ TTS-Fehler:", str(e))

    def speech_to_text(self, audio_file: str, sample_rate: int = 16000):
        if not self.stt_client:
            return

        if not os.path.exists(audio_file):
            print(f"❌ Datei nicht gefunden: {audio_file}")
            return

        with io.open(audio_file, "rb") as audio:
            content = audio.read()

        audio = speech.RecognitionAudio(content=content)

        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=sample_rate,
            language_code="de-DE"
        )

        try:
            response = self.stt_client.recognize(config=config, audio=audio)

            transcript = ""
            for result in response.results:
                transcript += result.alternatives[0].transcript + " "

            print("📝 Transkription:", transcript.strip())
            return transcript.strip()

        except Exception as e:
            print("❌ STT-Fehler:", str(e))
            return None

if __name__ == "__main__":
    converter = Converter()

    # Text → Sprache
    converter.text_to_speech("Dies ist ein kurzer Test der Google Sprachsynthese.")

    # Sprache → Text
    converter.speech_to_text("test_audio.wav")
