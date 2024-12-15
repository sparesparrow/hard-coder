# DictAssist

A sophisticated AI-powered personal assistant designed to capture, analyze, and remind you of your thoughts and ideas throughout the day. DictAssist combines voice interaction, natural language processing, and intelligent analysis to help you maintain and develop your ideas effectively.

## 🌟 Key Features

### 📝 Thought Capture
- Real-time voice-to-text conversion using Whisper
- Continuous listening mode with wake word detection
- Background noise reduction and voice activity detection
- Minimal latency (~600ms) for natural interaction

### 🤖 Evening Analysis
- Automated thought clustering and theme identification
- Pattern recognition across captured ideas
- Knowledge gap identification
- AI-generated insights and recommendations
- Semantic relationship mapping between thoughts

### ⏰ Smart Reminders
- Context-aware reminder system
- Priority-based notification scheduling
- Recurring reminders support
- Voice-controlled reminder creation
- Related thought suggestions

### 🗣️ Natural Voice Interaction
- High-quality text-to-speech using ElevenLabs
- Natural language command processing
- Multi-turn conversation support
- Contextual responses

## 🛠️ Technical Architecture

```
DictAssist/
├── core/
│   ├── thought_manager.py
│   ├── voice_interface.py
│   └── reminder_manager.py
├── analysis/
│   ├── thought_analyzer.py
│   └── evening_review.py
├── voice/
│   ├── stt_processor.py
│   └── tts_processor.py
├── utils/
│   ├── database.py
│   └── config.py
└── main.py
```

## 📋 Requirements

### System Requirements
- Python 3.8+
- SQLite3
- CUDA-compatible GPU (recommended for Whisper)

### API Keys
- OpenAI API key (for GPT-4)
- ElevenLabs API key (for TTS)

### Python Dependencies
```bash
pip install -r requirements.txt
```

## 🚀 Quick Start

1. Clone the repository:
```bash
git clone https://github.com/yourusername/DictAssist.git
cd DictAssist
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
export OPENAI_API_KEY="your-openai-key"
export ELEVENLABS_API_KEY="your-elevenlabs-key"
```

4. Run the assistant:
```bash
python main.py
```

## 💡 Usage Examples

### Capturing Thoughts
```python
# Voice command
"Start capture"
"Here's my idea about improving the project architecture..."
"End capture"
```

### Setting Reminders
```python
# Voice command
"Remind me to review the project proposal at 3 PM"
"Set a daily reminder to check emails at 9 AM"
```

### Evening Review
```python
# Voice command
"Start evening review"
# Assistant will provide:
# - Thought clusters and themes
# - Key patterns identified
# - Knowledge gaps
# - Action items
# - Learning opportunities
```

## 🔧 Configuration

### config.py
```python
class Config:
    ELEVENLABS_VOICE_ID = "josh"
    WHISPER_MODEL = "base"
    SAMPLE_RATE = 16000
    VAD_THRESHOLD = 0.3
    SILENCE_DURATION = 1.0
    
    # Wake words and commands
    WAKE_WORDS = ["hey assistant", "start capture"]
    END_CAPTURE_COMMANDS = ["end capture", "stop capture"]
    REVIEW_COMMANDS = ["evening review", "daily review"]
```

## 🎯 Features in Detail

### Thought Analysis
- Embedding-based thought clustering
- Theme identification using GPT-4
- Pattern recognition across thoughts
- Knowledge gap identification
- Action item generation

### Reminder System
- Priority levels (1-5)
- Recurring schedules (daily, weekly, monthly)
- Context-aware notifications
- Related thought suggestions
- AI-generated follow-up actions

### Voice Interface
- Wake word detection
- Continuous listening mode
- Background noise reduction
- Natural language understanding
- Multi-turn conversations

## 🔒 Privacy & Security

- Local processing of sensitive data
- Encrypted storage of thoughts and reminders
- Optional cloud backup
- Data export functionality
- GDPR-compliant data handling

## 🛣️ Roadmap

- [ ] Mobile app integration
- [ ] Multi-language support
- [ ] Custom wake word training
- [ ] Cloud sync capabilities
- [ ] Collaborative thought sharing
- [ ] Advanced analytics dashboard

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- OpenAI for Whisper and GPT-4
- ElevenLabs for TTS capabilities
- SentenceTransformers for semantic analysis
- The open-source community for various tools and libraries

## 📞 Support

For support, please open an issue in the GitHub repository or contact the maintainers at support@dictassist.com

## 🔗 Links

- [Documentation](https://dictassist.readthedocs.io/)
- [API Reference](https://dictassist.readthedocs.io/api)
- [Examples](https://dictassist.readthedocs.io/examples)
- [Contributing Guide](CONTRIBUTING.md)

---

Made with ❤️ by sparesparrow