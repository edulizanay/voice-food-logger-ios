import SwiftUI

/// Modal sheet for entering daily weight with validation and trend display
struct WeightInputSheet: View {
    @Binding var isPresented: Bool
    @State private var weightInput: String = ""
    @State private var isLoading: Bool = false
    @State private var errorMessage: String? = nil
    @State private var lastWeight: Double? = nil
    
    let onWeightSaved: () -> Void
    private let apiService = APIService()
    
    var body: some View {
        NavigationView {
            VStack(spacing: 24) {
                // Header section
                headerSection
                
                // Main input section  
                inputSection
                
                // Last weight display
                if let lastWeight = lastWeight {
                    lastWeightSection(lastWeight: lastWeight)
                }
                
                Spacer()
                
                // Action buttons
                buttonSection
            }
            .padding(.horizontal, 20)
            .padding(.top, 10)
            .navigationTitle("Log Weight")
            .navigationBarTitleDisplayMode(.inline)
            .navigationBarBackButtonHidden()
            .toolbar {
                ToolbarItem(placement: .navigationBarLeading) {
                    Button("Cancel") {
                        dismiss()
                    }
                    .foregroundColor(.secondary)
                }
            }
        }
        .onAppear {
            loadLastWeight()
            // Focus on the input field
            DispatchQueue.main.asyncAfter(deadline: .now() + 0.1) {
                // Input field will be focused automatically due to @FocusState if added
            }
        }
        .alert("Error", isPresented: .constant(errorMessage != nil)) {
            Button("OK") {
                errorMessage = nil
            }
        } message: {
            Text(errorMessage ?? "")
        }
    }
    
    // MARK: - Header Section
    
    private var headerSection: some View {
        VStack(spacing: 8) {
            Image(systemName: "scalemass.fill")
                .font(.largeTitle)
                .foregroundColor(.blue)
            
            Text("Today's Weight")
                .font(.title2)
                .fontWeight(.medium)
                .foregroundColor(.primary)
            
            Text("Enter your current weight in kilograms")
                .font(.subheadline)
                .foregroundColor(.secondary)
                .multilineTextAlignment(.center)
        }
        .padding(.top, 20)
    }
    
    // MARK: - Input Section
    
    private var inputSection: some View {
        VStack(spacing: 16) {
            HStack {
                TextField("0.0", text: $weightInput)
                    .font(.largeTitle)
                    .fontWeight(.semibold)
                    .multilineTextAlignment(.center)
                    .keyboardType(.decimalPad)
                    .textFieldStyle(.plain)
                    .frame(maxWidth: .infinity)
                
                Text("kg")
                    .font(.title2)
                    .foregroundColor(.secondary)
            }
            .padding(.horizontal, 20)
            .padding(.vertical, 16)
            .background(Color.gray.opacity(0.1))
            .cornerRadius(12)
            
            // Input validation feedback
            if !weightInput.isEmpty {
                inputValidationView
            }
        }
    }
    
    // MARK: - Input Validation
    
    private var inputValidationView: some View {
        Group {
            if let weight = Double(weightInput) {
                if weight < 20 || weight > 300 {
                    validationMessage("Weight must be between 20 and 300 kg", isError: true)
                } else {
                    validationMessage("✓ Valid weight entry", isError: false)
                }
            } else {
                validationMessage("Please enter a valid number", isError: true)
            }
        }
    }
    
    private func validationMessage(_ message: String, isError: Bool) -> some View {
        HStack {
            Image(systemName: isError ? "exclamationmark.triangle" : "checkmark.circle")
            Text(message)
        }
        .font(.caption)
        .foregroundColor(isError ? .red : .green)
    }
    
    // MARK: - Last Weight Section
    
    private func lastWeightSection(lastWeight: Double) -> some View {
        VStack(spacing: 12) {
            Divider()
            
            VStack(spacing: 8) {
                Text("Previous Entry")
                    .font(.subheadline)
                    .foregroundColor(.secondary)
                
                HStack(spacing: 16) {
                    VStack(alignment: .leading, spacing: 4) {
                        Text("Last Weight")
                            .font(.caption)
                            .foregroundColor(.secondary)
                        Text("\(lastWeight, specifier: "%.1f") kg")
                            .font(.headline)
                            .fontWeight(.medium)
                    }
                    
                    if let currentWeight = Double(weightInput), currentWeight > 0 {
                        VStack(alignment: .leading, spacing: 4) {
                            Text("Change")
                                .font(.caption)
                                .foregroundColor(.secondary)
                            
                            let difference = currentWeight - lastWeight
                            let isIncrease = difference > 0
                            let isDecrease = difference < 0
                            
                            HStack(spacing: 4) {
                                Image(systemName: isIncrease ? "arrow.up" : (isDecrease ? "arrow.down" : "minus"))
                                    .font(.caption)
                                    .foregroundColor(isIncrease ? .orange : (isDecrease ? .green : .gray))
                                
                                Text("\(abs(difference), specifier: "%.1f") kg")
                                    .font(.headline)
                                    .fontWeight(.medium)
                                    .foregroundColor(isIncrease ? .orange : (isDecrease ? .green : .gray))
                            }
                        }
                    }
                }
                .padding(.horizontal)
                .padding(.vertical, 12)
                .background(Color.gray.opacity(0.05))
                .cornerRadius(10)
            }
        }
    }
    
    // MARK: - Button Section
    
    private var buttonSection: some View {
        VStack(spacing: 12) {
            // Save button
            Button(action: saveWeight) {
                HStack {
                    if isLoading {
                        ProgressView()
                            .progressViewStyle(CircularProgressViewStyle(tint: .white))
                            .scaleEffect(0.8)
                    } else {
                        Image(systemName: "checkmark")
                            .font(.headline)
                    }
                    
                    Text(isLoading ? "Saving..." : "Save Weight")
                        .font(.headline)
                        .fontWeight(.medium)
                }
                .foregroundColor(.white)
                .frame(maxWidth: .infinity)
                .frame(height: 50)
                .background(canSave ? Color.blue : Color.gray)
                .cornerRadius(12)
            }
            .disabled(!canSave || isLoading)
            
            // Helpful tip
            Text("Tip: Weigh yourself at the same time each day for consistent tracking")
                .font(.caption)
                .foregroundColor(.secondary)
                .multilineTextAlignment(.center)
                .padding(.horizontal)
        }
        .padding(.bottom, 10)
    }
    
    // MARK: - Computed Properties
    
    private var canSave: Bool {
        guard let weight = Double(weightInput) else { return false }
        return weight >= 20 && weight <= 300
    }
    
    // MARK: - Methods
    
    private func loadLastWeight() {
        Task {
            do {
                let entries = try await apiService.getWeightEntries()
                if let lastEntry = entries.data.last {
                    await MainActor.run {
                        self.lastWeight = lastEntry.weightKg
                    }
                }
            } catch {
                await MainActor.run {
                    // Silently fail - last weight is optional info
                    self.lastWeight = nil
                }
            }
        }
    }
    
    private func saveWeight() {
        guard let weight = Double(weightInput), weight >= 20 && weight <= 300 else {
            errorMessage = "Please enter a valid weight between 20 and 300 kg"
            return
        }
        
        isLoading = true
        errorMessage = nil
        
        Task {
            do {
                _ = try await apiService.addWeightEntry(weightKg: weight)
                
                await MainActor.run {
                    // Haptic feedback for successful save
                    let impactFeedback = UIImpactFeedbackGenerator(style: .medium)
                    impactFeedback.impactOccurred()
                    
                    // Call completion handler and dismiss
                    onWeightSaved()
                    dismiss()
                }
            } catch {
                await MainActor.run {
                    isLoading = false
                    errorMessage = "Failed to save weight: \(error.localizedDescription)"
                }
            }
        }
    }
    
    private func dismiss() {
        // Hide keyboard first
        UIApplication.shared.sendAction(#selector(UIResponder.resignFirstResponder), to: nil, from: nil, for: nil)
        
        // Dismiss sheet
        withAnimation {
            isPresented = false
        }
    }
}

// MARK: - Preview

struct WeightInputSheet_Previews: PreviewProvider {
    static var previews: some View {
        WeightInputSheet(
            isPresented: .constant(true),
            onWeightSaved: { print("Weight saved!") }
        )
    }
}