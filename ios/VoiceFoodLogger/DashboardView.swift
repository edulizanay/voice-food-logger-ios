import SwiftUI
import AVFoundation
import UIKit

struct DashboardView: View {
    @StateObject private var audioRecorder = AudioRecorder()
    @StateObject private var apiService = APIService()
    
    @State private var showingPermissionAlert = false
    @State private var todaysTotals: Macros?
    @State private var todaysEntries: [FoodEntry] = []
    @State private var isLoadingData = false
    
    // Animated numbers state
    @State private var animatedCalories: Double = 0
    @State private var animatedProtein: Double = 0
    
    // Counter animation timers
    @State private var caloriesTimer: Timer?
    @State private var proteinTimer: Timer?
    
    // Edit modal state
    @State private var selectedEntry: FoodEntry?
    @State private var showingEditModal = false
    
    // Daily goals (hardcoded as requested)
    private let calorieGoal = 1800
    private let proteinGoal = 160.0
    
    var body: some View {
        NavigationView {
            VStack(spacing: 0) {
                
                // Daily Macros Header
                DailyMacrosHeaderView(
                    currentTotals: todaysTotals,
                    animatedCalories: animatedCalories,
                    animatedProtein: animatedProtein,
                    calorieGoal: calorieGoal,
                    proteinGoal: proteinGoal,
                    isLoading: isLoadingData
                )
                .padding(.horizontal, 20)
                .padding(.vertical, 16)
                
                Divider()
                
                // Today's Entries
                TodaysEntriesView(
                    entries: todaysEntries,
                    isLoading: isLoadingData,
                    apiService: apiService,
                    onEntryEdit: { entry in
                        selectedEntry = entry
                        showingEditModal = true
                    },
                    onDataChange: refreshData
                )
                
                Spacer(minLength: 20)
                
                // Recording Section
                RecordingSection(
                    audioRecorder: audioRecorder,
                    showingPermissionAlert: $showingPermissionAlert,
                    onRecordingComplete: refreshData
                )
                .padding(.horizontal, 20)
                .padding(.bottom, 30)
            }
            .navigationTitle("Food Tracker")
            .navigationBarTitleDisplayMode(.inline)
        }
        .sheet(isPresented: $showingEditModal) {
            if let entry = selectedEntry {
                EditQuantityModal(entry: entry, onUpdate: refreshData)
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
            refreshData()
        }
        .onDisappear {
            // Clean up timers
            caloriesTimer?.invalidate()
            proteinTimer?.invalidate()
        }
    }
    
    private func refreshData() {
        isLoadingData = true
        
        Task {
            do {
                // Fetch today's totals and entries in parallel
                async let totalsResponse = apiService.getTodayTotals()
                async let entriesResponse = apiService.getTodayEntries()
                
                let (totals, entries) = try await (totalsResponse, entriesResponse)
                
                await MainActor.run {
                    todaysTotals = totals.totals
                    todaysEntries = entries.entries
                    isLoadingData = false
                    
                    // Trigger animated counter updates
                    startCaloriesAnimation(from: animatedCalories, to: Double(totals.totals.calories))
                    startProteinAnimation(from: animatedProtein, to: totals.totals.proteinG)
                }
                
            } catch {
                await MainActor.run {
                    print("Failed to refresh data: \(error)")
                    isLoadingData = false
                }
            }
        }
    }
    
    // Progressive counter animation for calories
    private func startCaloriesAnimation(from startValue: Double, to endValue: Double) {
        caloriesTimer?.invalidate()
        
        guard startValue != endValue else {
            animatedCalories = endValue
            return
        }
        
        let startTime = Date()
        let totalDifference = endValue - startValue
        let duration: TimeInterval = 1.2
        
        caloriesTimer = Timer.scheduledTimer(withTimeInterval: 1.0/60.0, repeats: true) { timerInstance in
            let elapsed = Date().timeIntervalSince(startTime)
            let progress = min(elapsed / duration, 1.0)
            
            // Ease out curve (fast start, slow finish)
            let easedProgress = 1.0 - pow(1.0 - progress, 3.0)
            
            let currentValue = startValue + (totalDifference * easedProgress)
            animatedCalories = currentValue
            
            // Complete animation
            if progress >= 1.0 {
                animatedCalories = endValue
                timerInstance.invalidate()
                caloriesTimer = nil
            }
        }
    }
    
    // Progressive counter animation for protein
    private func startProteinAnimation(from startValue: Double, to endValue: Double) {
        proteinTimer?.invalidate()
        
        guard startValue != endValue else {
            animatedProtein = endValue
            return
        }
        
        let startTime = Date()
        let totalDifference = endValue - startValue
        let duration: TimeInterval = 1.2
        
        proteinTimer = Timer.scheduledTimer(withTimeInterval: 1.0/60.0, repeats: true) { timerInstance in
            let elapsed = Date().timeIntervalSince(startTime)
            let progress = min(elapsed / duration, 1.0)
            
            // Ease out curve (fast start, slow finish)
            let easedProgress = 1.0 - pow(1.0 - progress, 3.0)
            
            let currentValue = startValue + (totalDifference * easedProgress)
            animatedProtein = currentValue
            
            // Complete animation
            if progress >= 1.0 {
                animatedProtein = endValue
                timerInstance.invalidate()
                proteinTimer = nil
            }
        }
    }
}

struct DailyMacrosHeaderView: View {
    let currentTotals: Macros?
    let animatedCalories: Double
    let animatedProtein: Double
    let calorieGoal: Int
    let proteinGoal: Double
    let isLoading: Bool
    
    var body: some View {
        VStack(spacing: 16) {
            // Title
            HStack {
                Text("Today's Progress")
                    .font(.headline)
                    .foregroundColor(.primary)
                Spacer()
                if isLoading {
                    ProgressView()
                        .scaleEffect(0.8)
                }
            }
            
            // Macros Display
            if let totals = currentTotals {
                VStack(spacing: 12) {
                    // Calories
                    MacroProgressRow(
                        title: "Calories",
                        current: Int(animatedCalories),
                        goal: calorieGoal,
                        unit: "cal",
                        color: calorieProgressColor(current: Int(animatedCalories), goal: calorieGoal)
                    )
                    
                    // Protein
                    MacroProgressRow(
                        title: "Protein",
                        current: animatedProtein,
                        goal: proteinGoal,
                        unit: "g",
                        color: proteinProgressColor(current: animatedProtein, goal: proteinGoal)
                    )
                    
                    // Additional macros (smaller text)
                    HStack {
                        Text("Carbs: \(totals.carbsG, specifier: "%.1f")g")
                            .font(.caption)
                            .foregroundColor(.secondary)
                        
                        Spacer()
                        
                        Text("Fat: \(totals.fatG, specifier: "%.1f")g")
                            .font(.caption)
                            .foregroundColor(.secondary)
                    }
                }
            } else if !isLoading {
                Text("No entries yet today")
                    .font(.body)
                    .foregroundColor(.secondary)
            }
        }
        .padding()
        .background(Color(UIColor.systemGray6))
        .cornerRadius(12)
    }
    
    private func calorieProgressColor(current: Int, goal: Int) -> Color {
        let percentage = Double(current) / Double(goal)
        if percentage >= 0.8 { return .green }
        if percentage >= 0.5 { return .orange }
        return .blue
    }
    
    private func proteinProgressColor(current: Double, goal: Double) -> Color {
        let percentage = current / goal
        if percentage >= 0.8 { return .green }
        if percentage >= 0.5 { return .orange }
        return .blue
    }
}

struct MacroProgressRow: View {
    let title: String
    let current: Any
    let goal: Any
    let unit: String
    let color: Color
    
    var body: some View {
        HStack {
            Text(title)
                .font(.body)
                .fontWeight(.medium)
            
            Spacer()
            
            if let currentInt = current as? Int, let goalInt = goal as? Int {
                Text("\(currentInt) / \(goalInt) \(unit)")
                    .font(.body)
                    .fontWeight(.semibold)
                    .foregroundColor(color)
            } else if let currentDouble = current as? Double, let goalDouble = goal as? Double {
                Text("\(currentDouble, specifier: "%.1f") / \(goalDouble, specifier: "%.0f") \(unit)")
                    .font(.body)
                    .fontWeight(.semibold)
                    .foregroundColor(color)
            }
        }
    }
}

struct TodaysEntriesView: View {
    let entries: [FoodEntry]
    let isLoading: Bool
    let apiService: APIService
    let onEntryEdit: (FoodEntry) -> Void
    let onDataChange: () -> Void
    
    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            // Section Header
            HStack {
                Text("Today's Entries (\(entries.count))")
                    .font(.headline)
                    .padding(.horizontal, 20)
                    .padding(.top, 16)
                
                Spacer()
            }
            
            if isLoading {
                HStack {
                    Spacer()
                    ProgressView("Loading entries...")
                    Spacer()
                }
                .padding(.vertical, 40)
            } else if entries.isEmpty {
                VStack(spacing: 8) {
                    Image(systemName: "fork.knife")
                        .font(.system(size: 40))
                        .foregroundColor(.secondary)
                    
                    Text("No entries yet")
                        .font(.body)
                        .foregroundColor(.secondary)
                    
                    Text("Record your first meal below")
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
                .frame(maxWidth: .infinity)
                .padding(.vertical, 40)
            } else {
                List {
                    ForEach(entries) { entry in
                        EntryCard(entry: entry)
                            .swipeActions(edge: .trailing) {
                                Button("Delete", role: .destructive) {
                                    // Haptic feedback for delete action
                                    let impactFeedback = UIImpactFeedbackGenerator(style: .medium)
                                    impactFeedback.impactOccurred()
                                    deleteEntry(entry)
                                }
                            }
                            .swipeActions(edge: .leading) {
                                Button("Edit") {
                                    // Haptic feedback for edit action
                                    let impactFeedback = UIImpactFeedbackGenerator(style: .light)
                                    impactFeedback.impactOccurred()
                                    onEntryEdit(entry)
                                }
                                .tint(.blue)
                            }
                            .listRowSeparator(.hidden)
                            .listRowInsets(EdgeInsets(top: 4, leading: 20, bottom: 4, trailing: 20))
                    }
                }
                .listStyle(PlainListStyle())
            }
        }
    }
    
    private func deleteEntry(_ entry: FoodEntry) {
        Task {
            do {
                _ = try await apiService.deleteEntry(entryId: entry.id)
                await MainActor.run {
                    onDataChange() // Refresh the data
                }
            } catch {
                print("Error deleting entry: \(error)")
            }
        }
    }
}

struct EntryCard: View {
    let entry: FoodEntry
    
    private var entryTime: String {
        // Parse timestamp and format as time
        let formatter = DateFormatter()
        formatter.dateFormat = "yyyy-MM-dd'T'HH:mm:ss.SSSSSS"
        
        if let date = formatter.date(from: entry.timestamp) {
            let timeFormatter = DateFormatter()
            timeFormatter.dateFormat = "h:mm a"
            return timeFormatter.string(from: date)
        }
        return "Unknown time"
    }
    
    private var mealTypeDisplay: String {
        if let mealType = entry.mealType {
            return mealType.capitalized
        }
        return ""
    }
    
    private var totalCalories: Int {
        entry.items.compactMap { $0.macros?.calories }.reduce(0, +)
    }
    
    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            // Time, meal type and total calories
            HStack {
                HStack(spacing: 4) {
                    if let mealEmoji = entry.mealEmoji {
                        Text(mealEmoji)
                            .font(.caption)
                    }
                    
                    Text(entryTime)
                        .font(.caption)
                        .foregroundColor(.secondary)
                    
                    if !mealTypeDisplay.isEmpty {
                        Text("• \(mealTypeDisplay)")
                            .font(.caption)
                            .foregroundColor(.secondary)
                            .fontWeight(.medium)
                    }
                }
                
                Spacer()
                
                if totalCalories > 0 {
                    Text("\(totalCalories) cal")
                        .font(.caption)
                        .fontWeight(.semibold)
                        .foregroundColor(.blue)
                }
            }
            
            // Food items
            VStack(alignment: .leading, spacing: 4) {
                ForEach(Array(entry.items.enumerated()), id: \.offset) { _, item in
                    HStack {
                        Text(item.food)
                            .font(.body)
                            .fontWeight(.medium)
                        
                        Spacer()
                        
                        Text(item.quantity)
                            .font(.caption)
                            .foregroundColor(.secondary)
                    }
                }
            }
        }
        .padding(12)
        .background(Color(UIColor.systemBackground))
        .cornerRadius(8)
        .shadow(color: Color.black.opacity(0.05), radius: 2, x: 0, y: 1)
    }
}

struct RecordingSection: View {
    @ObservedObject var audioRecorder: AudioRecorder
    @Binding var showingPermissionAlert: Bool
    let onRecordingComplete: () -> Void
    
    var body: some View {
        VStack(spacing: 20) {
            
            // Status Display
            if audioRecorder.isRecording {
                VStack(spacing: 12) {
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
                    
                    Text(audioRecorder.formatTime(audioRecorder.recordingTime))
                        .font(.system(size: 24, weight: .medium, design: .monospaced))
                        .foregroundColor(.primary)
                }
            } else if audioRecorder.isProcessing {
                VStack(spacing: 12) {
                    HStack(spacing: 8) {
                        ProgressView()
                            .scaleEffect(0.8)
                        
                        Text(audioRecorder.processingStatus)
                            .font(.headline)
                            .foregroundColor(.blue)
                    }
                    
                    Text("Please wait...")
                        .font(.body)
                        .foregroundColor(.secondary)
                }
            } else if let error = audioRecorder.lastError {
                VStack(spacing: 12) {
                    HStack(spacing: 8) {
                        Image(systemName: audioRecorder.lastErrorType.iconName)
                            .foregroundColor(.orange)
                            .font(.title2)
                        
                        Text("Error")
                            .font(.headline)
                            .foregroundColor(.orange)
                    }
                    
                    Text(error)
                        .font(.system(size: 14))
                        .foregroundColor(.primary)
                        .multilineTextAlignment(.center)
                        .padding(.horizontal, 20)
                    
                    Text(audioRecorder.lastErrorType.suggestedAction)
                        .font(.system(size: 13))
                        .foregroundColor(.secondary)
                        .italic()
                }
            } else {
                Text("Ready to record your next meal")
                    .font(.body)
                    .foregroundColor(.secondary)
            }
            
            // Record Button
            Button(action: {
                if audioRecorder.hasPermission {
                    if audioRecorder.isRecording {
                        audioRecorder.stopRecording()
                    } else if audioRecorder.lastError != nil {
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
                        .frame(width: 80, height: 80)
                        .shadow(color: audioRecorder.isRecording ? .red.opacity(0.3) : .blue.opacity(0.3), radius: 8, x: 0, y: 4)
                    
                    if audioRecorder.isRecording {
                        RoundedRectangle(cornerRadius: 6)
                            .fill(Color.white)
                            .frame(width: 20, height: 20)
                    } else if audioRecorder.isProcessing {
                        ProgressView()
                            .progressViewStyle(CircularProgressViewStyle(tint: .white))
                            .scaleEffect(1.2)
                    } else {
                        Image(systemName: "mic.fill")
                            .font(.system(size: 28))
                            .foregroundColor(.white)
                    }
                }
            }
            .disabled(audioRecorder.isProcessing)
            .scaleEffect(audioRecorder.isRecording ? 1.1 : 1.0)
            .animation(.easeInOut(duration: 0.2), value: audioRecorder.isRecording)
            .opacity(audioRecorder.isProcessing ? 0.7 : 1.0)
            .onChange(of: audioRecorder.lastTranscription) { _, transcription in
                if !transcription.isEmpty && !audioRecorder.isProcessing {
                    // New entry was processed successfully
                    onRecordingComplete()
                    // Clear the results to prepare for next recording
                    DispatchQueue.main.asyncAfter(deadline: .now() + 1.0) {
                        audioRecorder.lastTranscription = ""
                        audioRecorder.lastFoodItems = []
                    }
                }
            }
            
            // Help Text
            Group {
                if audioRecorder.isRecording {
                    Text("Tap to stop recording")
                } else if audioRecorder.isProcessing {
                    Text("Processing your recording...")
                } else if audioRecorder.lastError != nil {
                    Text(audioRecorder.lastErrorType.suggestedAction)
                } else {
                    Text("Tap to start recording")
                }
            }
            .font(.caption)
            .foregroundColor(.secondary)
        }
    }
}

struct DashboardView_Previews: PreviewProvider {
    static var previews: some View {
        DashboardView()
    }
}