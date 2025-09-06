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
            
            recordingTimer = Timer.scheduledTimer(withTimeInterval: 0.1, repeats: true) { [weak self] _ in
                self?.updateRecordingTime()
            }
            
        } catch {
            print("Failed to start recording: \(error)")
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
            lastError = "No recording found to process"
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
                    lastError = error.localizedDescription
                }
            } catch {
                await MainActor.run {
                    isProcessing = false
                    processingStatus = ""
                    lastError = "Unexpected error: \(error.localizedDescription)"
                }
            }
        }
    }
    
    /// Clear the last error
    func clearError() {
        lastError = nil
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
        }
    }
    
    func audioRecorderEncodeErrorDidOccur(_ recorder: AVAudioRecorder, error: Error?) {
        if let error = error {
            print("Recording encode error: \(error)")
        }
    }
}