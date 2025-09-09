# 🎯 FitMe

A voice-powered food logging application with intelligent food parsing and nutrition tracking. Record your meals naturally and get detailed nutritional breakdowns instantly. **Now available as "FitMe" - your personal fitness and nutrition companion.**

## ✨ Features

- **🎙️ Voice Recording**: Natural speech-to-text food logging
- **🧠 AI Food Parsing**: Groq-powered intelligent food item extraction
- **📊 Nutrition Tracking**: Automatic macro calculation with database lookup
- **📱 iOS App**: Native SwiftUI interface with real-time feedback
- **🌐 Serverless Backend**: Vercel-deployed API for global accessibility
- **🗄️ Supabase Database**: Postgres storage with Row Level Security
- **📈 Daily Aggregation**: Track daily totals and progress

## 🏗️ Architecture

```
VoiceFoodLogger/
├── voice-food-logger-ios/  # iOS SwiftUI App
│   ├── VoiceFoodLogger/   # Main app module
│   │   ├── ContentView.swift      # Main recording interface
│   │   ├── AudioRecorder.swift    # Audio recording & Vercel integration
│   │   ├── APIService.swift       # Serverless API communication
│   │   ├── Models.swift          # Data models (FoodItem, etc.)
│   │   └── ResultsView.swift     # Results display
│   └── VoiceFoodLogger.xcodeproj
├── backend/                # Serverless API Functions
│   ├── api/               # Vercel endpoints
│   │   ├── voice-upload.py       # Audio processing endpoint
│   │   ├── today-entries.py      # Daily entries retrieval
│   │   ├── today-totals.py       # Daily totals calculation
│   │   └── health.py             # Health check endpoint
│   ├── shared/            # Shared modules
│   │   ├── transcription.py     # Groq Whisper integration
│   │   ├── processing.py        # AI food parsing logic
│   │   ├── meal_detection.py    # Meal categorization
│   │   ├── supabase_storage.py  # Database operations
│   │   └── data/nutrition_db.json  # Nutrition database
│   ├── templates/         # Web interface
│   │   └── index.html     # Dashboard template
│   ├── app.py            # Local development server
│   └── vercel.json       # Deployment configuration
```

## 🚀 Getting Started

### Prerequisites

- **macOS** with Xcode 16+
- **Python 3.8+** (for local development)
- **Groq API Key** (for AI processing)
- **Supabase Account** (for database storage)

### Backend Setup

The backend is deployed on Vercel and uses Supabase for data storage. For local development:

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure environment variables in .env
echo "GROQ_API_KEY=your_groq_api_key_here" > .env
echo "SUPABASE_URL=your_supabase_project_url" >> .env
echo "SUPABASE_KEY=your_supabase_anon_key" >> .env

# Start local development server
python app.py
```

### Production Deployment

The app uses:
- **Vercel**: Global serverless API deployment
- **Supabase**: Postgres database with Row Level Security
- **Production API**: `https://voice-food-logger-ios.vercel.app`

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

1. **Launch the iOS app** (production backend is already deployed)
2. **Grant microphone permission** when prompted
3. **Tap the microphone button** to start recording
4. **Speak naturally**: "I ate 150 grams of chicken and half a cup of rice"
5. **View results**: Automatic transcription, parsing, and nutrition calculation
6. **Access web dashboard**: Visit the Vercel deployment for web interface

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
- **Serverless deployment** on Vercel with global CDN
- **CORS-enabled** API endpoints for iOS integration
- **Supabase integration** with session-based entry grouping
- **Multipart audio upload** handling
- **Daily aggregation** with automatic macro summation
- **Row Level Security** for future user authentication
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
✅ **Vercel Serverless Deployment**  
✅ **Supabase Database Integration**  
✅ **Global Production Scaling**

The system is **fully functional** with voice recording, AI processing, and nutrition tracking working seamlessly together. **Now deployed globally with Supabase database and branded as FitMe with improved user experience.**

## 📝 Recent Updates (September 2025)

- **🎯 FitMe Rebranding**: Changed app name from VoiceFoodLogger to FitMe
- **🐛 Critical Delete Fix**: Entries now permanently deleted (legacy entries support)
- **🔄 SwiftUI Architecture**: Converted ScrollView to List for native swipe actions  
- **🎨 App Icon Infrastructure**: Set up professional icon system
- **📱 iPhone Testing**: Successfully deployed and tested on physical device
- **⚡ Enhanced UI**: Timer-based animated counters with smooth transitions
- **🌐 Vercel Deployment**: Migrated to serverless functions for global scaling
- **🗄️ Supabase Integration**: Replaced JSON storage with Postgres database
- **🧹 Codebase Cleanup**: Removed legacy files and duplicate modules

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
