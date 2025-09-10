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

// MARK: - Weight Tracking Models

/// Represents a weight entry
struct WeightEntry: Codable, Identifiable {
    let id: Int
    let weightKg: Double
    let createdAt: String
    let notes: String?
    
    enum CodingKeys: String, CodingKey {
        case id
        case weightKg = "weight_kg"  
        case createdAt = "created_at"
        case notes
    }
}

/// Represents user goals for weight and nutrition
struct UserGoals: Codable {
    let id: Int?
    let calorieGoal: Int
    let proteinGoal: Double
    let weightGoalKg: Double
    let createdAt: String?
    let updatedAt: String?
    
    enum CodingKeys: String, CodingKey {
        case id
        case calorieGoal = "calorie_goal"
        case proteinGoal = "protein_goal"
        case weightGoalKg = "weight_goal_kg"
        case createdAt = "created_at"
        case updatedAt = "updated_at"
    }
}

/// Chart data point for visualizations
struct ChartDataPoint: Identifiable, Equatable {
    let id = UUID()
    let date: Date
    let value: Double
    let goalValue: Double?
    
    static func == (lhs: ChartDataPoint, rhs: ChartDataPoint) -> Bool {
        return lhs.id == rhs.id
    }
}

/// Time period for chart data
enum TimePeriod: String, CaseIterable {
    case today = "today"
    case week = "week"
    case month = "month"
    
    var displayName: String {
        switch self {
        case .today: return "Today"
        case .week: return "This Week"
        case .month: return "This Month"
        }
    }
}

/// Weight chart data structure
struct WeightChartData {
    let weightPoints: [ChartDataPoint]
    let goalWeight: Double?
    let period: TimePeriod
    let isEmpty: Bool
    
    static var empty: WeightChartData {
        WeightChartData(
            weightPoints: [],
            goalWeight: nil,
            period: .week,
            isEmpty: true
        )
    }
}

/// Calorie chart data structure
struct CalorieChartData {
    let caloriePoints: [ChartDataPoint]
    let goalCalories: Int
    let period: TimePeriod
    let isEmpty: Bool
    
    static var empty: CalorieChartData {
        CalorieChartData(
            caloriePoints: [],
            goalCalories: 1800,
            period: .week,
            isEmpty: true
        )
    }
}

// MARK: - Weight Tracking API Responses

/// Response for weight entries
struct WeightEntriesResponse: APIResponse {
    let success: Bool
    let data: [WeightEntry]
    let count: Int
}

/// Response for user goals
struct UserGoalsResponse: APIResponse {
    let success: Bool
    let data: UserGoals
}

/// Response for weight history
struct WeightHistoryResponse: APIResponse {
    let success: Bool
    let data: [WeightHistoryPoint]
    let period: String
    let count: Int
}

/// Weight history data point
struct WeightHistoryPoint: Codable {
    let date: String
    let weightKg: Double
    let goalWeightKg: Double?
    let entryId: Int?
    
    enum CodingKeys: String, CodingKey {
        case date
        case weightKg = "weight_kg"
        case goalWeightKg = "goal_weight_kg"
        case entryId = "entry_id"
    }
}

/// Response for calorie history
struct CalorieHistoryResponse: APIResponse {
    let success: Bool
    let data: [CalorieHistoryPoint]
    let period: String
    let count: Int
}

/// Calorie history data point
struct CalorieHistoryPoint: Codable {
    let date: String
    let calories: Int
    let goalCalories: Int
    let proteinG: Double
    let carbsG: Double
    let fatG: Double
    
    enum CodingKeys: String, CodingKey {
        case date, calories
        case goalCalories = "goal_calories"
        case proteinG = "protein_g"
        case carbsG = "carbs_g"
        case fatG = "fat_g"
    }
}

// MARK: - Request Models

