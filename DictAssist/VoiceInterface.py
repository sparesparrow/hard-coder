
import whisper
from elevenlabs import generate, play, set_api_key
import sounddevice as sd
import soundfile as sf
import numpy as np
from datetime import datetime
import threading
import queue
import tempfile
import os
from typing import Optional

class VoiceInterface:
    def __init__(self, elevenlabs_api_key: str):
        self.whisper_model = whisper.load_model("base")
        set_api_key(elevenlabs_api_key)
        
        self.audio_queue = queue.Queue()
        self.recording = False
        self.sample_rate = 16000

    def start_recording(self):
        """Start continuous recording in a separate thread"""
        self.recording = True
        threading.Thread(target=self._record_audio).start()

    def stop_recording(self) -> Optional[str]:
        """Stop recording and transcribe the audio"""
        self.recording = False
        
        # Collect all audio chunks from queue
        audio_chunks = []
        while not self.audio_queue.empty():
            audio_chunks.append(self.audio_queue.get())
        
        if not audio_chunks:
            return None

        # Combine audio chunks and save temporarily
        audio_data = np.concatenate(audio_chunks)
        temp_file = tempfile.mktemp(suffix=".wav")
        sf.write(temp_file, audio_data, self.sample_rate)

        # Transcribe with Whisper
        result = self.whisper_model.transcribe(temp_file)
        os.remove(temp_file)
        
        return result["text"]

    def _record_audio(self):
        """Record audio in chunks"""
        def callback(indata, frames, time, status):
            if status:
                print(status)
            self.audio_queue.put(indata.copy())

        with sd.InputStream(callback=callback,
                          channels=1,
                          samplerate=self.sample_rate):
            while self.recording:
                sd.sleep(100)

    def speak(self, text: str):
        """Convert text to speech using ElevenLabs"""
        audio = generate(
            text=text,
            voice="Josh",  # Choose appropriate voice
            model="eleven_monolingual_v1"
        )
        play(audio)

class EnhancedAssistant:
    def __init__(self, elevenlabs_api_key: str):
        self.thought_manager = ThoughtManager()
        self.voice_interface = VoiceInterface(elevenlabs_api_key)
        self.active = False

    def start_listening(self):
        """Start listening for voice input"""
        self.active = True
        self.voice_interface.speak("I'm listening for your thoughts.")
        self.voice_interface.start_recording()

    def stop_listening(self):
        """Stop listening and process the recorded thought"""
        transcribed_text = self.voice_interface.stop_recording()
        if transcribed_text:
            self.thought_manager.add_thought(transcribed_text)
            self.voice_interface.speak("Thought captured successfully.")
        return transcribed_text

    def evening_review(self):
        """Provide spoken evening review"""
        thoughts = self.thought_manager.get_todays_thoughts()
        
        if not thoughts:
            review_text = "You haven't captured any thoughts today."
        else:
            review_text = "Here's your thought review for today. "
            for thought in thoughts:
                review_text += f"You noted: {thought['content']}. "
                # Add AI-generated suggestions
                review_text += self._generate_suggestion(thought['content'])
        
        self.voice_interface.speak(review_text)
        return review_text

    def _generate_suggestion(self, thought: str) -> str:
        """Generate improvement suggestions for a thought"""
        # This could be enhanced with LLM integration
        return "Consider exploring this topic in more detail. "

class VoiceControlledAssistant:
    def __init__(self, elevenlabs_api_key: str):
        self.assistant = EnhancedAssistant(elevenlabs_api_key)
        self.command_mode = False

    def run(self):
        """Main loop for voice-controlled operation"""
        self.assistant.voice_interface.speak("Hello! I'm ready to help you capture your thoughts.")
        
        while True:
            try:
                if not self.command_mode:
                    # Listen for wake word or command
                    self.assistant.voice_interface.start_recording()
                    transcribed = self.assistant.voice_interface.stop_recording()
                    
                    if transcribed:
                        if "start capture" in transcribed.lower():
                            self.command_mode = True
                            self.assistant.start_listening()
                        elif "evening review" in transcribed.lower():
                            self.assistant.evening_review()
                        elif "exit" in transcribed.lower():
                            self.assistant.voice_interface.speak("Goodbye!")
                            break
                else:
                    # Capture thought mode
                    transcribed = self.assistant.stop_listening()
                    if "end capture" in transcribed.lower():
                        self.command_mode = False
                        self.assistant.voice_interface.speak("Stopped capturing thoughts.")
                    
            except Exception as e:
                print(f"Error: {e}")
                self.assistant.voice_interface.speak("Sorry, there was an error. Please try again.")

def main():
    # Load API key from environment variable or config file
    elevenlabs_api_key = os.getenv("ELEVENLABS_API_KEY")
    
    assistant = VoiceControlledAssistant(elevenlabs_api_key)
    assistant.run()

if __name__ == "__main__":
    main()