import SwiftUI
import AVFoundation

struct ContentView: View {
    @StateObject private var audioRecorder = AudioRecorder()
    @State private var showingPermissionAlert = false
    
    var body: some View {
        NavigationView {
            VStack(spacing: 40) {
                Spacer()
                
                // App Title
                VStack(spacing: 8) {
                    Image(systemName: "mic.fill")
                        .font(.system(size: 60))
                        .foregroundColor(.blue)
                    
                    Text("Voice Food Logger")
                        .font(.largeTitle)
                        .fontWeight(.bold)
                        .multilineTextAlignment(.center)
                    
                    Text("Tap to record your food intake")
                        .font(.subheadline)
                        .foregroundColor(.secondary)
                        .multilineTextAlignment(.center)
                }
                
                Spacer()
                
                // Status Display
                if audioRecorder.isRecording {
                    VStack(spacing: 16) {
                        // Recording Animation
                        HStack(spacing: 8) {
                            Circle()
                                .fill(Color.red)
                                .frame(width: 8, height: 8)
                                .scaleEffect(audioRecorder.isRecording ? 1.5 : 1.0)
                                .animation(.easeInOut(duration: 0.5).repeatForever(), value: audioRecorder.isRecording)
                            
                            Text("Recording...")
                                .font(.headline)
                                .foregroundColor(.red)
                        }
                        
                        // Recording Time
                        Text(audioRecorder.formatTime(audioRecorder.recordingTime))
                            .font(.system(size: 32, weight: .medium, design: .monospaced))
                            .foregroundColor(.primary)
                    }
                } else if audioRecorder.isProcessing {
                    VStack(spacing: 16) {
                        // Processing Animation
                        HStack(spacing: 8) {
                            ProgressView()
                                .scaleEffect(0.8)
                            
                            Text(audioRecorder.processingStatus)
                                .font(.headline)
                                .foregroundColor(.blue)
                        }
                        
                        Text("Please wait...")
                            .font(.system(size: 18, weight: .medium))
                            .foregroundColor(.secondary)
                    }
                } else if !audioRecorder.lastTranscription.isEmpty {
                    VStack(spacing: 16) {
                        // Success State
                        HStack(spacing: 8) {
                            Image(systemName: "checkmark.circle.fill")
                                .foregroundColor(.green)
                                .font(.title2)
                            
                            Text("Processing Complete!")
                                .font(.headline)
                                .foregroundColor(.green)
                        }
                        
                        // Results Summary
                        Text("\(audioRecorder.lastFoodItems.count) food items logged")
                            .font(.system(size: 18, weight: .medium))
                            .foregroundColor(.primary)
                    }
                } else if let error = audioRecorder.lastError {
                    VStack(spacing: 16) {
                        // Error State
                        HStack(spacing: 8) {
                            Image(systemName: "exclamationmark.triangle.fill")
                                .foregroundColor(.orange)
                                .font(.title2)
                            
                            Text("Processing Failed")
                                .font(.headline)
                                .foregroundColor(.orange)
                        }
                        
                        Text("Tap to retry")
                            .font(.system(size: 18, weight: .medium))
                            .foregroundColor(.secondary)
                    }
                } else {
                    VStack(spacing: 16) {
                        Text("Ready to Record")
                            .font(.headline)
                            .foregroundColor(.secondary)
                        
                        Text("00:00.0")
                            .font(.system(size: 32, weight: .medium, design: .monospaced))
                            .foregroundColor(.secondary)
                    }
                }
                
                Spacer()
                
                // Record Button
                Button(action: {
                    if audioRecorder.hasPermission {
                        if audioRecorder.isRecording {
                            audioRecorder.stopRecording()
                        } else if audioRecorder.lastError != nil {
                            // Clear error and start fresh recording
                            audioRecorder.clearError()
                            audioRecorder.startRecording()
                        } else {
                            audioRecorder.startRecording()
                        }
                    } else {
                        showingPermissionAlert = true
                    }
                }) {
                    ZStack {
                        Circle()
                            .fill(audioRecorder.isRecording ? Color.red : Color.blue)
                            .frame(width: 120, height: 120)
                            .shadow(color: audioRecorder.isRecording ? .red.opacity(0.3) : .blue.opacity(0.3), radius: 10, x: 0, y: 5)
                        
                        if audioRecorder.isRecording {
                            RoundedRectangle(cornerRadius: 8)
                                .fill(Color.white)
                                .frame(width: 30, height: 30)
                        } else if audioRecorder.isProcessing {
                            ProgressView()
                                .progressViewStyle(CircularProgressViewStyle(tint: .white))
                                .scaleEffect(1.5)
                        } else {
                            Image(systemName: "mic.fill")
                                .font(.system(size: 40))
                                .foregroundColor(.white)
                        }
                    }
                }
                .disabled(audioRecorder.isProcessing)
                .scaleEffect(audioRecorder.isRecording ? 1.1 : 1.0)
                .animation(.easeInOut(duration: 0.2), value: audioRecorder.isRecording)
                .opacity(audioRecorder.isProcessing ? 0.7 : 1.0)
                
                Spacer()
                
                // Help Text
                Group {
                    if audioRecorder.isRecording {
                        Text("Tap to stop recording")
                    } else if audioRecorder.isProcessing {
                        Text("Processing your recording...")
                    } else if audioRecorder.lastError != nil {
                        Text("Tap to try recording again")
                    } else if !audioRecorder.lastTranscription.isEmpty {
                        Text("Tap to record more food")
                    } else {
                        Text("Tap to start recording")
                    }
                }
                .font(.caption)
                .foregroundColor(.secondary)
                .padding(.bottom, 20)
            }
            .padding(.horizontal, 30)
            .navigationBarHidden(true)
        }
        .sheet(isPresented: .constant(!audioRecorder.lastTranscription.isEmpty && !audioRecorder.isProcessing)) {
            ResultsView(transcription: audioRecorder.lastTranscription, 
                       foodItems: audioRecorder.lastFoodItems) {
                // Clear results when dismissing
                audioRecorder.lastTranscription = ""
                audioRecorder.lastFoodItems = []
            }
        }
        .alert("Microphone Permission Required", isPresented: $showingPermissionAlert) {
            Button("Settings") {
                if let settingsUrl = URL(string: UIApplication.openSettingsURLString) {
                    UIApplication.shared.open(settingsUrl)
                }
            }
            Button("Cancel", role: .cancel) { }
        } message: {
            Text("Please enable microphone access in Settings to record audio.")
        }
        .onAppear {
            audioRecorder.requestPermission()
        }
    }
}

struct ContentView_Previews: PreviewProvider {
    static var previews: some View {
        ContentView()
    }
}
