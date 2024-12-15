
class Config:
    ELEVENLABS_VOICE_ID = "josh"  # Replace with preferred voice ID
    WHISPER_MODEL = "base"  # Can be "tiny", "base", "small", "medium", "large"
    SAMPLE_RATE = 16000
    VAD_THRESHOLD = 0.3
    SILENCE_DURATION = 1.0  # seconds of silence to trigger end of speech

    # Wake words and commands
    WAKE_WORDS = ["hey assistant", "start capture"]
    END_CAPTURE_COMMANDS = ["end capture", "stop capture"]
    REVIEW_COMMANDS = ["evening review", "daily review"]