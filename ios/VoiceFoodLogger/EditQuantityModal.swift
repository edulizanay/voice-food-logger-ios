import SwiftUI

struct EditQuantityModal: View {
    let entry: FoodEntry
    @StateObject private var apiService = APIService()
    
    @Environment(\.dismiss) private var dismiss
    @State private var selectedQuantity: Int = 150
    @State private var isUpdating = false
    @State private var showingDeleteConfirmation = false
    
    // Callback to refresh the parent view
    let onUpdate: () -> Void
    
    var body: some View {
        NavigationView {
            VStack(spacing: 20) {
                // Header
                Text("Edit Quantity")
                    .font(.title2)
                    .fontWeight(.semibold)
                    .padding(.top)
                
                // Food name
                if let firstItem = entry.items.first {
                    Text(firstItem.food.capitalized)
                        .font(.title3)
                        .foregroundColor(.secondary)
                }
                
                Spacer()
                
                // Picker wheel
                VStack {
                    Text("Quantity")
                        .font(.headline)
                        .foregroundColor(.primary)
                    
                    Picker("Quantity", selection: $selectedQuantity) {
                        ForEach(1...2000, id: \.self) { quantity in
                            Text("\(quantity)g")
                                .tag(quantity)
                        }
                    }
                    .pickerStyle(WheelPickerStyle())
                    .frame(height: 150)
                    .onChange(of: selectedQuantity) { _ in
                        updateQuantity()
                    }
                }
                
                Spacer()
                
                // Delete button
                Button(action: {
                    showingDeleteConfirmation = true
                }) {
                    HStack {
                        Image(systemName: "trash")
                        Text("Delete Entry")
                    }
                    .foregroundColor(.white)
                    .frame(maxWidth: .infinity)
                    .padding()
                    .background(Color.red)
                    .cornerRadius(10)
                }
                .padding(.horizontal)
                .alert("Delete Entry", isPresented: $showingDeleteConfirmation) {
                    Button("Cancel", role: .cancel) { }
                    Button("Delete", role: .destructive) {
                        deleteEntry()
                    }
                } message: {
                    Text("Are you sure you want to delete this food entry? This action cannot be undone.")
                }
                
                Spacer()
            }
            .padding()
            .navigationBarHidden(true)
        }
        .onAppear {
            setupInitialQuantity()
        }
        .disabled(isUpdating)
        .overlay {
            if isUpdating {
                Color.black.opacity(0.1)
                    .ignoresSafeArea()
                ProgressView()
                    .scaleEffect(1.5)
            }
        }
    }
    
    private func setupInitialQuantity() {
        guard let firstItem = entry.items.first else { return }
        
        // Extract number from quantity string (e.g., "150g" -> 150)
        let quantityString = firstItem.quantity
        let numbers = quantityString.components(separatedBy: CharacterSet.decimalDigits.inverted).joined()
        if let quantity = Int(numbers), quantity >= 1 && quantity <= 2000 {
            selectedQuantity = quantity
        }
    }
    
    private func updateQuantity() {
        guard !isUpdating else { return }
        
        Task {
            await MainActor.run {
                isUpdating = true
            }
            
            do {
                let newQuantity = "\(selectedQuantity)g"
                _ = try await apiService.updateEntry(entryId: entry.id, newQuantity: newQuantity)
                
                await MainActor.run {
                    onUpdate() // Refresh parent view
                    isUpdating = false
                }
            } catch {
                await MainActor.run {
                    isUpdating = false
                    print("Error updating entry: \(error)")
                }
            }
        }
    }
    
    private func deleteEntry() {
        Task {
            await MainActor.run {
                isUpdating = true
            }
            
            do {
                _ = try await apiService.deleteEntry(entryId: entry.id)
                
                await MainActor.run {
                    onUpdate() // Refresh parent view
                    dismiss() // Close modal
                }
            } catch {
                await MainActor.run {
                    isUpdating = false
                    print("Error deleting entry: \(error)")
                }
            }
        }
    }
}

// Preview
struct EditQuantityModal_Previews: PreviewProvider {
    static var previews: some View {
        EditQuantityModal(
            entry: FoodEntry(
                id: "test-id",
                timestamp: "2023-09-08T10:30:00",
                items: [
                    FoodItem(
                        food: "chicken breast",
                        quantity: "150g",
                        macros: Macros(calories: 248, proteinG: 46.5, carbsG: 0.0, fatG: 5.4)
                    )
                ]
            ),
            onUpdate: {}
        )
    }
}