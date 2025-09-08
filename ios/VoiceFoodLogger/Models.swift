import Foundation

// MARK: - Core Data Models

/// Represents nutritional macros for a food item
struct Macros: Codable {
    let calories: Int
    let proteinG: Double
    let carbsG: Double
    let fatG: Double
    
    enum CodingKeys: String, CodingKey {
        case calories
        case proteinG = "protein_g"
        case carbsG = "carbs_g" 
        case fatG = "fat_g"
    }
}

/// Represents a single food item with quantity and nutritional information
struct FoodItem: Codable {
    let food: String
    let quantity: String
    let macros: Macros?
    
    enum CodingKeys: String, CodingKey {
        case food, quantity, macros
    }
}

/// Represents a food entry with timestamp and items
struct FoodEntry: Codable {
    let timestamp: String
    let items: [FoodItem]
}


// MARK: - API Response Models

/// Base API response structure
protocol APIResponse: Codable {
    var success: Bool { get }
}

/// Success response for audio processing
struct AudioProcessResponse: APIResponse {
    let success: Bool
    let transcription: String
    let items: [FoodItem]
    let timestamp: String
}

/// Response for entries retrieval
struct EntriesResponse: APIResponse {
    let success: Bool
    let date: String
    let entries: [FoodEntry]
}

/// Response for daily totals
struct DailyTotalsResponse: APIResponse {
    let success: Bool
    let date: String
    let totals: Macros
}


/// Error response
struct ErrorResponse: APIResponse, Error {
    let success: Bool = false
    let error: String
}

// MARK: - Request Models

