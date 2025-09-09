import SwiftUI

struct EditQuantityModal: View {
    let entry: FoodEntry
    @StateObject private var apiService = APIService()
    
    @Environment(\.dismiss) private var dismiss
    @State private var itemQuantities: [String: Int] = [:]
    @State private var isUpdating = false
    @State private var showingDeleteConfirmation = false
    
    // Callback to refresh the parent view
    let onUpdate: () -> Void
    
    // Initialize itemQuantities immediately to prevent blank modal on first launch
    init(entry: FoodEntry, onUpdate: @escaping () -> Void) {
        self.entry = entry
        self.onUpdate = onUpdate
        
        // Pre-populate itemQuantities before UI renders
        var initialQuantities: [String: Int] = [:]
        for item in entry.items {
            let quantityString = item.quantity
            let numbers = quantityString.components(separatedBy: CharacterSet.decimalDigits.inverted).joined()
            if let quantity = Int(numbers), quantity >= 1 && quantity <= 2000 {
                initialQuantities[item.food] = quantity
            } else {
                initialQuantities[item.food] = 150
            }
        }
        self._itemQuantities = State(initialValue: initialQuantities)
    }
    
    var body: some View {
        NavigationView {
            VStack(spacing: 20) {
                // Header
                Text("Edit Items")
                    .font(.title2)
                    .fontWeight(.semibold)
                    .padding(.top)
                
                // Show all items in the session
                ScrollView {
                    VStack(spacing: 16) {
                        ForEach(Array(entry.items.enumerated()), id: \.offset) { index, item in
                            VStack(alignment: .leading, spacing: 8) {
                                Text(item.food.capitalized)
                                    .font(.headline)
                                    .foregroundColor(.primary)
                                
                                // Quantity picker for this item
                                HStack {
                                    Text("Quantity:")
                                        .font(.subheadline)
                                        .foregroundColor(.secondary)
                                    
                                    Picker("Quantity", selection: Binding(
                                        get: { itemQuantities[item.food] ?? 150 },
                                        set: { newValue in
                                            itemQuantities[item.food] = newValue
                                            updateQuantities()
                                        }
                                    )) {
                                        ForEach(1...2000, id: \.self) { quantity in
                                            Text("\(quantity)g")
                                                .tag(quantity)
                                        }
                                    }
                                    .pickerStyle(MenuPickerStyle())
                                }
                                
                                Divider()
                            }
                            .padding(.horizontal)
                        }
                    }
                }
                .frame(maxHeight: 300)
                
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
    
    private func updateQuantities() {
        guard !isUpdating else { return }
        
        Task {
            await MainActor.run {
                isUpdating = true
            }
            
            do {
                // Build array of item updates
                let itemUpdates = itemQuantities.map { (food, quantity) in
                    ["food": food, "quantity": "\(quantity)g"]
                }
                
                _ = try await apiService.updateEntryItems(entryId: entry.id, itemUpdates: itemUpdates)
                
                await MainActor.run {
                    onUpdate() // Refresh parent view
                    isUpdating = false
                }
            } catch {
                await MainActor.run {
                    isUpdating = false
                    print("Error updating entry items: \(error)")
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