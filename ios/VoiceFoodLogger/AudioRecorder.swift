import Foundation
import AVFoundation
import SwiftUI

class AudioRecorder: NSObject, ObservableObject {
    // MARK: - Recording State
    @Published var isRecording = false
    @Published var recordingTime: TimeInterval = 0
    @Published var hasPermission = false
    
    // MARK: - Backend Integration State
    @Published var isProcessing = false
    @Published var processingStatus = ""
    @Published var lastTranscription = ""
    @Published var lastFoodItems: [FoodItem] = []
    @Published var lastError: String?
    @Published var lastErrorType: RecordingErrorType = .unknown
    
    // MARK: - Services
    private let apiService = APIService()
    
    private var audioRecorder: AVAudioRecorder?
    private var recordingTimer: Timer?
    private var audioSession: AVAudioSession!
    private var lastRecordingURL: URL?
    
    override init() {
        super.init()
        self.audioSession = AVAudioSession.sharedInstance()
        setupAudioSession()
        requestPermission()
    }
    
    private func setupAudioSession() {
        do {
            try audioSession.setCategory(.playAndRecord, mode: .default)
            try audioSession.setActive(true)
        } catch {
            print("Failed to setup audio session: \(error)")
        }
    }
    
    func requestPermission() {
        audioSession.requestRecordPermission { [weak self] allowed in
            DispatchQueue.main.async {
                self?.hasPermission = allowed
            }
        }
    }
    
    func startRecording() {
        guard hasPermission else {
            requestPermission()
            return
        }
        
        let documentsPath = FileManager.default.urls(for: .documentDirectory, in: .userDomainMask)[0]
        let audioFilename = documentsPath.appendingPathComponent("recording-\(Date().timeIntervalSince1970).m4a")
        
        let settings: [String: Any] = [
            AVFormatIDKey: Int(kAudioFormatMPEG4AAC),
            AVSampleRateKey: 44100,
            AVNumberOfChannelsKey: 1,
            AVEncoderAudioQualityKey: AVAudioQuality.high.rawValue
        ]
        
        do {
            audioRecorder = try AVAudioRecorder(url: audioFilename, settings: settings)
            audioRecorder?.delegate = self
            audioRecorder?.record()
            
            // Store the recording URL for later backend processing
            lastRecordingURL = audioFilename
            
            isRecording = true
            recordingTime = 0
            
            // Clear previous results
            lastTranscription = ""
            lastFoodItems = []
            lastError = nil
            lastErrorType = .unknown
            
            recordingTimer = Timer.scheduledTimer(withTimeInterval: 0.1, repeats: true) { [weak self] _ in
                self?.updateRecordingTime()
            }
            
        } catch {
            print("Failed to start recording: \(error)")
            lastError = "Unable to start recording. Please check microphone permissions."
            lastErrorType = .recordingFailed
        }
    }
    
    func stopRecording() {
        audioRecorder?.stop()
        recordingTimer?.invalidate()
        recordingTimer = nil
        isRecording = false
        
        // Start backend processing
        processRecordingWithBackend()
    }
    
    // MARK: - Backend Integration
    
    private func processRecordingWithBackend() {
        guard let recordingURL = lastRecordingURL else {
            lastError = "No recording found. Please try again."
            lastErrorType = .noRecording
            return
        }
        
        // Check recording file exists and has content
        do {
            let fileAttributes = try FileManager.default.attributesOfItem(atPath: recordingURL.path)
            let fileSize = fileAttributes[.size] as? Int64 ?? 0
            
            if fileSize < 1024 { // Less than 1KB
                lastError = "Recording too short. Please speak longer."
                lastErrorType = .recordingTooShort
                return
            }
        } catch {
            lastError = "Unable to access recording. Please try again."
            lastErrorType = .fileAccessError
            return
        }
        
        isProcessing = true
        processingStatus = "Processing audio..."
        
        Task {
            do {
                processingStatus = "Transcribing audio..."
                let response = try await apiService.processAudio(audioURL: recordingURL)
                
                await MainActor.run {
                    processingStatus = "Processing complete!"
                    lastTranscription = response.transcription
                    lastFoodItems = response.items
                    isProcessing = false
                    lastError = nil
                }
                
                // Clear processing status after a short delay
                try? await Task.sleep(nanoseconds: 2_000_000_000) // 2 seconds
                await MainActor.run {
                    processingStatus = ""
                }
                
            } catch let error as APIError {
                await MainActor.run {
                    isProcessing = false
                    processingStatus = ""
                    
                    // Provide user-friendly error messages based on API error type
                    switch error {
                    case .networkError:
                        lastError = "Connection failed. Check your internet and try again."
                        lastErrorType = .networkError
                    case .serverError(let message):
                        if message.lowercased().contains("transcription") {
                            lastError = "Could not understand the recording. Please speak clearly."
                            lastErrorType = .transcriptionFailed
                        } else if message.lowercased().contains("parsing") || message.lowercased().contains("food") {
                            lastError = "Could not identify food items. Try describing them differently."
                            lastErrorType = .parsingFailed
                        } else {
                            lastError = "Server error: \(message)"
                            lastErrorType = .serverError
                        }
                    case .httpError(let code):
                        if code == 413 {
                            lastError = "Recording too large. Try a shorter recording."
                            lastErrorType = .recordingTooLarge
                        } else if code >= 500 {
                            lastError = "Server is temporarily unavailable. Please try again."
                            lastErrorType = .serverError
                        } else {
                            lastError = "Request failed (Error \(code)). Please try again."
                            lastErrorType = .httpError
                        }
                    case .invalidResponse, .decodingError:
                        lastError = "Received invalid data. Please try again."
                        lastErrorType = .invalidResponse
                    }
                }
            } catch {
                await MainActor.run {
                    isProcessing = false
                    processingStatus = ""
                    
                    // Handle system errors
                    let nsError = error as NSError
                    if nsError.domain == NSURLErrorDomain {
                        switch nsError.code {
                        case NSURLErrorNotConnectedToInternet:
                            lastError = "No internet connection. Please check your settings."
                            lastErrorType = .noInternet
                        case NSURLErrorTimedOut:
                            lastError = "Request timed out. Please try again."
                            lastErrorType = .timeout
                        case NSURLErrorCannotConnectToHost:
                            lastError = "Cannot connect to server. Please try again later."
                            lastErrorType = .cannotConnect
                        default:
                            lastError = "Connection error. Please check your network."
                            lastErrorType = .networkError
                        }
                    } else {
                        lastError = "Unexpected error occurred. Please try again."
                        lastErrorType = .unknown
                    }
                }
            }
        }
    }
    
    /// Clear the last error
    func clearError() {
        lastError = nil
        lastErrorType = .unknown
    }
    
    private func updateRecordingTime() {
        guard let recorder = audioRecorder else { return }
        recordingTime = recorder.currentTime
    }
    
    func formatTime(_ time: TimeInterval) -> String {
        let minutes = Int(time) / 60
        let seconds = Int(time) % 60
        let milliseconds = Int((time.truncatingRemainder(dividingBy: 1)) * 10)
        return String(format: "%02d:%02d.%d", minutes, seconds, milliseconds)
    }
}

extension AudioRecorder: AVAudioRecorderDelegate {
    func audioRecorderDidFinishRecording(_ recorder: AVAudioRecorder, successfully flag: Bool) {
        if flag {
            print("Recording saved to: \(recorder.url)")
        } else {
            print("Recording failed")
            DispatchQueue.main.async { [weak self] in
                self?.lastError = "Recording failed. Please try again."
                self?.lastErrorType = .recordingFailed
                self?.isProcessing = false
            }
        }
    }
    
    func audioRecorderEncodeErrorDidOccur(_ recorder: AVAudioRecorder, error: Error?) {
        if let error = error {
            print("Recording encode error: \(error)")
            DispatchQueue.main.async { [weak self] in
                self?.lastError = "Audio encoding failed. Please try again."
                self?.lastErrorType = .encodingError
                self?.isProcessing = false
            }
        }
    }
}

// MARK: - Error Types

/// Types of errors that can occur during recording and processing
enum RecordingErrorType {
    case unknown
    case recordingFailed
    case noRecording
    case recordingTooShort
    case recordingTooLarge
    case fileAccessError
    case encodingError
    case networkError
    case noInternet
    case timeout
    case cannotConnect
    case serverError
    case httpError
    case invalidResponse
    case transcriptionFailed
    case parsingFailed
    
    /// Suggested action for the user based on error type
    var suggestedAction: String {
        switch self {
        case .recordingTooShort:
            return "Speak for at least 2 seconds"
        case .recordingTooLarge:
            return "Keep recordings under 2 minutes"
        case .noInternet, .networkError, .cannotConnect:
            return "Check your network connection"
        case .timeout:
            return "Try a shorter recording"
        case .transcriptionFailed:
            return "Speak clearly and avoid background noise"
        case .parsingFailed:
            return "Describe food items more specifically"
        case .serverError:
            return "Wait a moment and try again"
        default:
            return "Tap to try again"
        }
    }
    
    /// Icon system name for the error type
    var iconName: String {
        switch self {
        case .noInternet, .networkError, .cannotConnect:
            return "wifi.slash"
        case .recordingFailed, .noRecording, .encodingError:
            return "mic.slash"
        case .recordingTooShort, .recordingTooLarge:
            return "waveform.badge.exclamationmark"
        case .timeout:
            return "clock.badge.exclamationmark"
        case .serverError, .httpError:
            return "server.rack"
        case .transcriptionFailed, .parsingFailed:
            return "text.badge.xmark"
        default:
            return "exclamationmark.triangle"
        }
    }
}