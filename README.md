# Voice Food Logger iOS App

A SwiftUI-based iOS application for voice-based food logging.

## Project Structure

```
VoiceFoodLogger.xcodeproj/          # Xcode project file
VoiceFoodLogger/                    # Main app target
├── VoiceFoodLoggerApp.swift        # App entry point  
├── ContentView.swift               # Main UI with voice recording
├── AudioRecorder.swift             # Audio recording logic
├── Assets.xcassets/                # App icons and assets
│   ├── AccentColor.colorset/       # App accent color
│   └── AppIcon.appiconset/         # App icon assets
VoiceFoodLoggerTests/               # Unit tests
VoiceFoodLoggerUITests/             # UI tests
README.md                           # Project documentation
```

## Features

- ✅ SwiftUI interface with animated record button
- ✅ Voice recording using AVFoundation
- ✅ Real-time recording timer
- ✅ Microphone permission handling
- ✅ M4A audio file output
- ✅ iOS 16.0+ deployment target
- ✅ Full Xcode project with tests

## Building the App

### Using Xcode (Recommended)
1. Open `VoiceFoodLogger.xcodeproj` in Xcode
2. Add microphone permissions:
   - Select the project in Navigator
   - Go to VoiceFoodLogger target → Info tab
   - Under "Custom iOS Target Properties", add:
   - Key: `Privacy - Microphone Usage Description`
   - Value: `This app needs access to the microphone to record your food descriptions.`
3. Select iPhone simulator or device
4. Press Cmd+R to build and run

### Command Line Build
```bash
xcodebuild -scheme VoiceFoodLogger -project VoiceFoodLogger.xcodeproj -destination 'platform=iOS Simulator,name=iPhone 16' build
```

## Code Overview

### VoiceFoodLoggerApp.swift
Main app entry point using SwiftUI's `@main` attribute.

### ContentView.swift
Primary UI featuring:
- Large animated record button with visual feedback
- Real-time recording timer
- Microphone permission handling alerts
- Clean, accessible SwiftUI design

### AudioRecorder.swift
Core recording functionality:
- AVFoundation-based audio recording
- Microphone permission management  
- M4A file format output with timestamps
- Real-time recording state updates
- Timer-based UI updates

## Audio Files
Recorded audio files are saved to the app's Documents directory as M4A files with timestamps in the format: `recording-{timestamp}.m4a`

## Troubleshooting

### Build Issues
- If you get "Multiple commands produce Info.plist" error, make sure you haven't manually added an Info.plist file to the project
- Microphone permissions should be added through Xcode's project settings, not a manual Info.plist

### Simulator Issues
- Voice recording works in iOS Simulator but uses simulated audio input
- For real microphone testing, use a physical device
- Make sure the selected simulator supports your target iOS version

## Next Steps
The app is ready for backend integration to process the recorded audio files for food logging functionality.