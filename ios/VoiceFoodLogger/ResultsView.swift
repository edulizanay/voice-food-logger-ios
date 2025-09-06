import SwiftUI

struct ResultsView: View {
    let transcription: String
    let foodItems: [FoodItem]
    let onDismiss: () -> Void
    
    var body: some View {
        NavigationView {
            ScrollView {
                VStack(alignment: .leading, spacing: 24) {
                    
                    // Success Header
                    VStack(spacing: 12) {
                        Image(systemName: "checkmark.circle.fill")
                            .font(.system(size: 48))
                            .foregroundColor(.green)
                        
                        Text("Food Logged Successfully!")
                            .font(.title2)
                            .fontWeight(.bold)
                            .multilineTextAlignment(.center)
                        
                        Text("Your food has been processed and added to today's log")
                            .font(.subheadline)
                            .foregroundColor(.secondary)
                            .multilineTextAlignment(.center)
                    }
                    .frame(maxWidth: .infinity)
                    .padding(.top, 20)
                    
                    Divider()
                    
                    // Transcription Section
                    VStack(alignment: .leading, spacing: 12) {
                        Label("What I Heard", systemImage: "waveform")
                            .font(.headline)
                            .foregroundColor(.blue)
                        
                        Text(transcription)
                            .font(.body)
                            .padding()
                            .background(Color(UIColor.systemGray6))
                            .cornerRadius(12)
                    }
                    
                    // Food Items Section
                    VStack(alignment: .leading, spacing: 12) {
                        Label("Food Items (\\(foodItems.count))", systemImage: "list.bullet")
                            .font(.headline)
                            .foregroundColor(.green)
                        
                        LazyVStack(spacing: 8) {
                            ForEach(Array(foodItems.enumerated()), id: \.offset) { index, item in
                                FoodItemRow(item: item)
                            }
                        }
                    }
                    
                    // Summary Section
                    if let totalMacros = calculateTotalMacros() {
                        VStack(alignment: .leading, spacing: 12) {
                            Label("Nutrition Summary", systemImage: "chart.bar.fill")
                                .font(.headline)
                                .foregroundColor(.purple)
                            
                            MacrosSummaryView(macros: totalMacros)
                        }
                    }
                    
                    Spacer()
                }
                .padding(.horizontal, 20)
                .padding(.bottom, 20)
            }
            .navigationTitle("Food Entry Results")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button("Done") {
                        onDismiss()
                    }
                    .fontWeight(.semibold)
                }
            }
        }
    }
    
    private func calculateTotalMacros() -> Macros? {
        guard !foodItems.isEmpty else { return nil }
        
        var totalCalories = 0
        var totalProtein = 0.0
        var totalCarbs = 0.0
        var totalFat = 0.0
        
        for item in foodItems {
            if let macros = item.macros {
                totalCalories += macros.calories
                totalProtein += macros.proteinG
                totalCarbs += macros.carbsG
                totalFat += macros.fatG
            }
        }
        
        return Macros(
            calories: totalCalories,
            proteinG: totalProtein,
            carbsG: totalCarbs,
            fatG: totalFat
        )
    }
}

struct FoodItemRow: View {
    let item: FoodItem
    
    var body: some View {
        HStack {
            VStack(alignment: .leading, spacing: 4) {
                Text(item.food)
                    .font(.body)
                    .fontWeight(.medium)
                
                Text(item.quantity)
                    .font(.caption)
                    .foregroundColor(.secondary)
            }
            
            Spacer()
            
            if let macros = item.macros {
                VStack(alignment: .trailing, spacing: 2) {
                    Text("\\(macros.calories) cal")
                        .font(.caption)
                        .fontWeight(.semibold)
                        .foregroundColor(.primary)
                    
                    HStack(spacing: 8) {
                        Text("P: \\(macros.proteinG, specifier: \"%.1f\")g")
                            .font(.caption2)
                            .foregroundColor(.blue)
                        
                        Text("C: \\(macros.carbsG, specifier: \"%.1f\")g")
                            .font(.caption2)
                            .foregroundColor(.orange)
                        
                        Text("F: \\(macros.fatG, specifier: \"%.1f\")g")
                            .font(.caption2)
                            .foregroundColor(.green)
                    }
                }
            }
        }
        .padding(.horizontal, 16)
        .padding(.vertical, 12)
        .background(Color(UIColor.systemBackground))
        .cornerRadius(8)
        .shadow(color: Color.black.opacity(0.05), radius: 2, x: 0, y: 1)
    }
}

struct MacrosSummaryView: View {
    let macros: Macros
    
    var body: some View {
        VStack(spacing: 12) {
            // Total Calories
            HStack {
                Text("Total Calories")
                    .font(.headline)
                Spacer()
                Text("\\(macros.calories)")
                    .font(.title2)
                    .fontWeight(.bold)
                    .foregroundColor(.primary)
            }
            
            Divider()
            
            // Macros Breakdown
            HStack(spacing: 20) {
                MacroView(name: "Protein", value: macros.proteinG, unit: "g", color: .blue)
                MacroView(name: "Carbs", value: macros.carbsG, unit: "g", color: .orange)
                MacroView(name: "Fat", value: macros.fatG, unit: "g", color: .green)
            }
        }
        .padding()
        .background(Color(UIColor.systemGray6))
        .cornerRadius(12)
    }
}

struct MacroView: View {
    let name: String
    let value: Double
    let unit: String
    let color: Color
    
    var body: some View {
        VStack(spacing: 4) {
            Text("\\(value, specifier: \"%.1f\")")
                .font(.title3)
                .fontWeight(.bold)
                .foregroundColor(color)
            
            Text(unit)
                .font(.caption2)
                .foregroundColor(color)
            
            Text(name)
                .font(.caption)
                .foregroundColor(.secondary)
        }
        .frame(maxWidth: .infinity)
    }
}

struct ResultsView_Previews: PreviewProvider {
    static var previews: some View {
        ResultsView(
            transcription: "I ate 100 grams of chicken breast and half a cup of rice",
            foodItems: [
                FoodItem(
                    food: "chicken breast",
                    quantity: "100 grams",
                    macros: Macros(calories: 165, proteinG: 31.0, carbsG: 0.0, fatG: 3.6)
                ),
                FoodItem(
                    food: "rice",
                    quantity: "0.5 cup",
                    macros: Macros(calories: 103, proteinG: 2.1, carbsG: 22.0, fatG: 0.2)
                )
            ],
            onDismiss: {}
        )
    }
}