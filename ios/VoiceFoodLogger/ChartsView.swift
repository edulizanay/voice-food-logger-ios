import SwiftUI

/// Main analytics screen displaying weight and calorie charts
struct ChartsView: View {
    @StateObject private var apiService = APIService()
    @State private var weightData: WeightChartData = .empty
    @State private var calorieData: CalorieChartData = .empty
    @State private var selectedPeriod: TimePeriod = .week
    @State private var showingWeightInput = false
    @State private var isLoading = false
    @State private var loadingError: String? = nil
    
    var body: some View {
        ScrollView {
            VStack(spacing: 24) {
                // Header with period selector
                headerSection
                
                // Main content
                if isLoading {
                    loadingView
                } else if let error = loadingError {
                    errorView(error)
                } else {
                    chartsContent
                }
            }
            .padding(.horizontal, 16)
            .padding(.vertical, 20)
        }
        .refreshable {
            await loadData()
        }
        .onAppear {
            Task { await loadData() }
        }
        .sheet(isPresented: $showingWeightInput) {
            WeightInputSheet(
                isPresented: $showingWeightInput,
                onWeightSaved: {
                    Task { await loadData() }
                }
            )
        }
    }
    
    // MARK: - Header Section
    
    private var headerSection: some View {
        VStack(spacing: 16) {
            // Title
            HStack {
                Text("Analytics")
                    .font(.largeTitle)
                    .fontWeight(.bold)
                    .foregroundColor(.primary)
                
                Spacer()
                
                // Refresh button
                Button(action: {
                    Task { await loadData() }
                }) {
                    Image(systemName: "arrow.clockwise")
                        .font(.title3)
                        .foregroundColor(.blue)
                        .rotationEffect(.degrees(isLoading ? 360 : 0))
                        .animation(
                            isLoading ? .linear(duration: 1).repeatForever(autoreverses: false) : .default,
                            value: isLoading
                        )
                }
                .disabled(isLoading)
            }
            
            // Period selector
            TimePeriodPicker(selectedPeriod: $selectedPeriod)
                .onChange(of: selectedPeriod) { _ in
                    Task { await loadData() }
                }
        }
    }
    
    // MARK: - Charts Content
    
    private var chartsContent: some View {
        VStack(spacing: 32) {
            // Weight chart section
            weightChartSection
            
            // Calorie chart section
            calorieChartSection
            
            // Bottom spacing for swipe navigation
            Color.clear
                .frame(height: 50)
        }
    }
    
    // MARK: - Weight Chart Section
    
    private var weightChartSection: some View {
        VStack(alignment: .leading, spacing: 16) {
            HStack {
                VStack(alignment: .leading, spacing: 4) {
                    Text("Weight Progress")
                        .font(.title2)
                        .fontWeight(.semibold)
                        .foregroundColor(.primary)
                    
                    if !weightData.isEmpty {
                        Text("\(weightData.weightPoints.count) entries")
                            .font(.caption)
                            .foregroundColor(.secondary)
                    }
                }
                
                Spacer()
                
                // Add weight button
                Button(action: { showingWeightInput = true }) {
                    HStack(spacing: 6) {
                        Image(systemName: "plus.circle.fill")
                            .font(.title3)
                        Text("Add")
                            .font(.subheadline)
                            .fontWeight(.medium)
                    }
                    .foregroundColor(.blue)
                    .padding(.horizontal, 12)
                    .padding(.vertical, 6)
                    .background(Color.blue.opacity(0.1))
                    .cornerRadius(20)
                }
            }
            
            WeightChart(data: weightData)
                .frame(height: 220)
                .background(Color.white)
                .cornerRadius(16)
                .shadow(color: .black.opacity(0.05), radius: 8, x: 0, y: 2)
        }
    }
    
    // MARK: - Calorie Chart Section
    
    private var calorieChartSection: some View {
        VStack(alignment: .leading, spacing: 16) {
            VStack(alignment: .leading, spacing: 4) {
                Text("Calorie Intake")
                    .font(.title2)
                    .fontWeight(.semibold)
                    .foregroundColor(.primary)
                
                if !calorieData.isEmpty {
                    let avgCalories = calorieData.caloriePoints.map { $0.value }.reduce(0, +) / Double(calorieData.caloriePoints.count)
                    Text("Avg: \(Int(avgCalories)) cal/day")
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
            }
            
            CalorieChart(data: calorieData)
                .frame(height: 220)
                .background(Color.white)
                .cornerRadius(16)
                .shadow(color: .black.opacity(0.05), radius: 8, x: 0, y: 2)
        }
    }
    
    // MARK: - Loading View
    
    private var loadingView: some View {
        VStack(spacing: 32) {
            ForEach(0..<2, id: \.self) { _ in
                VStack(alignment: .leading, spacing: 16) {
                    HStack {
                        RoundedRectangle(cornerRadius: 6)
                            .fill(Color.gray.opacity(0.3))
                            .frame(width: 120, height: 20)
                        
                        Spacer()
                        
                        RoundedRectangle(cornerRadius: 12)
                            .fill(Color.gray.opacity(0.3))
                            .frame(width: 60, height: 30)
                    }
                    
                    RoundedRectangle(cornerRadius: 16)
                        .fill(Color.gray.opacity(0.1))
                        .frame(height: 220)
                        .overlay(
                            ProgressView()
                                .progressViewStyle(CircularProgressViewStyle())
                        )
                }
            }
        }
        .redacted(reason: .placeholder)
        .animation(.easeInOut(duration: 1.2).repeatForever(autoreverses: true), value: isLoading)
    }
    
    // MARK: - Error View
    
    private func errorView(_ error: String) -> some View {
        VStack(spacing: 20) {
            Image(systemName: "exclamationmark.triangle")
                .font(.largeTitle)
                .foregroundColor(.orange)
            
            Text("Unable to Load Charts")
                .font(.headline)
                .foregroundColor(.primary)
            
            Text(error)
                .font(.subheadline)
                .foregroundColor(.secondary)
                .multilineTextAlignment(.center)
                .padding(.horizontal)
            
            Button("Retry") {
                Task { await loadData() }
            }
            .buttonStyle(.borderedProminent)
        }
        .padding(.vertical, 60)
    }
    
    // MARK: - Data Loading
    
    @MainActor
    private func loadData() async {
        isLoading = true
        loadingError = nil
        
        // Add a small delay to show loading state
        try? await Task.sleep(nanoseconds: 300_000_000)
        
        async let weightTask = loadWeightData()
        async let calorieTask = loadCalorieData()
        
        await weightTask
        await calorieTask
        
        isLoading = false
    }
    
    @MainActor
    private func loadWeightData() async {
        do {
            let data = try await apiService.getWeightChartData(period: selectedPeriod)
            weightData = data
        } catch {
            loadingError = "Failed to load weight data: \(error.localizedDescription)"
            weightData = .empty
        }
    }
    
    @MainActor
    private func loadCalorieData() async {
        do {
            let data = try await apiService.getCalorieChartData(period: selectedPeriod)
            calorieData = data
        } catch {
            loadingError = "Failed to load calorie data: \(error.localizedDescription)"
            calorieData = .empty
        }
    }
}

// MARK: - Time Period Picker

struct TimePeriodPicker: View {
    @Binding var selectedPeriod: TimePeriod
    
    var body: some View {
        Picker("Time Period", selection: $selectedPeriod) {
            ForEach(TimePeriod.allCases, id: \.self) { period in
                Text(period.displayName)
                    .tag(period)
            }
        }
        .pickerStyle(.segmented)
        .background(Color.gray.opacity(0.1))
        .cornerRadius(8)
    }
}

// MARK: - Preview

struct ChartsView_Previews: PreviewProvider {
    static var previews: some View {
        ChartsView()
            .preferredColorScheme(.light)
        
        ChartsView()
            .preferredColorScheme(.dark)
    }
}