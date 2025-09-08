# 🎯 FitMe

A voice-powered food logging application with intelligent food parsing and nutrition tracking. Record your meals naturally and get detailed nutritional breakdowns instantly. **Now available as "FitMe" - your personal fitness and nutrition companion.**

## ✨ Features

- **🎙️ Voice Recording**: Natural speech-to-text food logging
- **🧠 AI Food Parsing**: Groq-powered intelligent food item extraction
- **📊 Nutrition Tracking**: Automatic macro calculation with database lookup
- **📱 iOS App**: Native SwiftUI interface with real-time feedback
- **🌐 Flask Backend**: Robust API for audio processing and food analysis
- **📈 Daily Aggregation**: Track daily totals and progress

## 🏗️ Architecture

```
VoiceFoodLogger/
├── ios/                    # iOS SwiftUI App
│   ├── VoiceFoodLogger/   # Main app module
│   │   ├── ContentView.swift      # Main recording interface
│   │   ├── AudioRecorder.swift    # Audio recording & backend integration
│   │   ├── APIService.swift       # Flask API communication
│   │   ├── Models.swift          # Data models (FoodItem, etc.)
│   │   └── ResultsView.swift     # Results display
│   └── VoiceFoodLogger.xcodeproj
├── backend/                # Flask API Server
│   ├── app.py             # Main Flask application
│   ├── processing.py      # AI food parsing logic
│   ├── processing/prompts/
│   │   └── parser.yaml    # LLM prompts for food parsing
│   ├── data/
│   │   └── nutrition_db.json  # Nutrition database
│   └── logs/              # Daily JSON logs
└── shared/                # Shared configuration
    └── config.yaml
```

## 🚀 Getting Started

### Prerequisites

- **macOS** with Xcode 16+
- **Python 3.8+**
- **Groq API Key** (for AI processing)

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Add your Groq API key to .env
echo "GROQ_API_KEY=your_groq_api_key_here" > .env

# Start the server
python app.py
```

### iOS App Setup

```bash
cd ios
# Build and run on simulator
xcodebuild -scheme VoiceFoodLogger -project VoiceFoodLogger.xcodeproj \
  -destination 'platform=iOS Simulator,name=iPhone 16,OS=18.6'

# Install on simulator
xcrun simctl install "iPhone 16" path/to/VoiceFoodLogger.app
xcrun simctl launch "iPhone 16" com.eduardolizana.voicefoodlogger.VoiceFoodLogger
```

## 🎯 Usage

1. **Start the backend server**: `python backend/app.py`
2. **Launch the iOS app** in simulator or device
3. **Grant microphone permission** when prompted
4. **Tap the microphone button** to start recording
5. **Speak naturally**: "I ate 150 grams of chicken and half a cup of rice"
6. **View results**: Automatic transcription, parsing, and nutrition calculation

## 🧠 AI Pipeline

1. **🎙️ Voice Recording** → iOS AVAudioRecorder captures M4A audio
2. **📝 Transcription** → Groq Whisper converts speech to text
3. **🔍 Food Parsing** → Groq Qwen extracts structured food items
4. **📊 Nutrition Lookup** → Database provides macro calculations
5. **📱 Results Display** → iOS shows detailed breakdown

## 🛠️ Technical Details

### LLM Integration
- **Whisper**: Speech-to-text transcription
- **Qwen 32B**: Food parsing with thinking/response tags
- **Structured Output**: JSON extraction with fallback handling

### Backend Features
- **CORS-enabled** Flask API for iOS integration
- **Multipart audio upload** handling
- **Daily aggregation** with automatic macro summation
- **Error handling** with detailed logging
- **Nutrition database** with partial matching

### iOS Features
- **Real-time UI states**: Recording, Processing, Success, Error
- **Audio permissions**: Automatic permission handling
- **Network integration**: Robust API communication
- **Sheet presentation**: Results display with dismiss handling

## 🎨 UI States

- **🏠 Idle**: Ready to record with microphone icon
- **🎤 Recording**: Red pulsing animation with live timer
- **⚙️ Processing**: Blue spinner with status updates
- **✅ Success**: Green checkmark with results summary
- **❌ Error**: Orange warning with retry option

## 🔧 Build Commands

```bash
# Standard build (recommended)
xcodebuild -scheme VoiceFoodLogger -project VoiceFoodLogger.xcodeproj \
  -destination 'platform=iOS Simulator,name=iPhone 16,OS=18.6'

# Clean build
xcodebuild clean -project VoiceFoodLogger.xcodeproj -scheme VoiceFoodLogger

# Install and launch
xcrun simctl install "iPhone 16" path/to/app
xcrun simctl launch "iPhone 16" com.eduardolizana.voicefoodlogger.VoiceFoodLogger
```

## 📊 Example Usage

**Input**: "I had two eggs and a banana for breakfast"

**Backend Processing**:
```json
{
  "transcription": "I had two eggs and a banana for breakfast",
  "items": [
    {
      "food": "eggs",
      "quantity": "2 pieces",
      "macros": {"calories": 140, "protein_g": 12.0, "carbs_g": 1.0, "fat_g": 10.0}
    },
    {
      "food": "banana", 
      "quantity": "1 piece",
      "macros": {"calories": 105, "protein_g": 1.3, "carbs_g": 27.0, "fat_g": 0.3}
    }
  ],
  "total_calories": 245,
  "total_macros": {"protein_g": 13.3, "carbs_g": 28.0, "fat_g": 10.3}
}
```

## 🔍 Status

✅ **Complete Monorepo Migration**  
✅ **iOS-Backend Integration**  
✅ **Voice Recording & Processing**  
✅ **AI Food Parsing with Groq**  
✅ **Nutrition Database Lookup**  
✅ **Daily Logging & Aggregation**  
✅ **FitMe App Rebranding**  
✅ **Delete Bug Fixes**  
✅ **SwiftUI Architecture Fix**

The system is **fully functional** with voice recording, AI processing, and nutrition tracking working seamlessly together. **Now branded as FitMe with improved user experience.**

## 📝 Recent Updates (September 2025)

- **🎯 FitMe Rebranding**: Changed app name from VoiceFoodLogger to FitMe
- **🐛 Critical Delete Fix**: Entries now permanently deleted (legacy entries support)
- **🔄 SwiftUI Architecture**: Converted ScrollView to List for native swipe actions  
- **🎨 App Icon Infrastructure**: Set up professional icon system
- **📱 iPhone Testing**: Successfully deployed and tested on physical device
- **⚡ Enhanced UI**: Timer-based animated counters with smooth transitions

## 🤝 Contributing

This is a personal food logging project. The codebase demonstrates:
- iOS/SwiftUI development patterns
- Flask API design
- AI/LLM integration techniques
- Audio processing workflows
- Nutrition data management

---

*Built with ❤️ using SwiftUI, Flask, and Groq AI*
# Manual deployment trigger Mon Sep  8 20:51:52 CEST 2025
