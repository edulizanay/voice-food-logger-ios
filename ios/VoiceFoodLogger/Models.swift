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
struct FoodEntry: Codable, Identifiable {
    let id: String
    let timestamp: String
    let mealType: String?
    let mealEmoji: String?
    let items: [FoodItem]
    
    enum CodingKeys: String, CodingKey {
        case id, timestamp, items
        case mealType = "meal_type"
        case mealEmoji = "meal_emoji"
    }
    
    // Regular initializer for creating entries in code
    init(id: String, timestamp: String, items: [FoodItem], mealType: String? = nil, mealEmoji: String? = nil) {
        self.id = id
        self.timestamp = timestamp
        self.mealType = mealType
        self.mealEmoji = mealEmoji
        self.items = items
    }
    
    // Custom decoder to handle entries with or without IDs and meal types
    init(from decoder: Decoder) throws {
        let container = try decoder.container(keyedBy: CodingKeys.self)
        // Use timestamp as fallback ID for entries without ID
        let decodedId = try container.decodeIfPresent(String.self, forKey: .id)
        let timestamp = try container.decode(String.self, forKey: .timestamp)
        self.id = decodedId ?? timestamp
        self.timestamp = timestamp
        self.mealType = try container.decodeIfPresent(String.self, forKey: .mealType)
        self.mealEmoji = try container.decodeIfPresent(String.self, forKey: .mealEmoji)
        self.items = try container.decode([FoodItem].self, forKey: .items)
    }
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


/// Basic success response
struct BasicResponse: APIResponse {
    let success: Bool
    let message: String?
}

/// Error response
struct ErrorResponse: APIResponse, Error {
    let success: Bool = false
    let error: String
}

// MARK: - Request Models

