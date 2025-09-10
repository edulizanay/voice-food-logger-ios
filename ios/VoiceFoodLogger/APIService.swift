import Foundation

/// Service for communicating with the Voice Food Logger Flask backend
class APIService: ObservableObject {
    
    // MARK: - Configuration
    
    /// Base URL for the Vercel serverless backend (global access)
    private let baseURL = "https://voice-food-logger-ios.vercel.app"
    
    /// URLSession for making HTTP requests
    private let urlSession: URLSession
    
    /// JSON decoder configured for the backend response format
    private let jsonDecoder: JSONDecoder
    
    /// JSON encoder for request bodies
    private let jsonEncoder: JSONEncoder
    
    // MARK: - Initialization
    
    init() {
        // Configure URL session with reasonable timeouts
        let config = URLSessionConfiguration.default
        config.timeoutIntervalForRequest = 30.0
        config.timeoutIntervalForResource = 60.0
        self.urlSession = URLSession(configuration: config)
        
        // Configure JSON decoder
        self.jsonDecoder = JSONDecoder()
        
        // Configure JSON encoder
        self.jsonEncoder = JSONEncoder()
    }
    
    // MARK: - Audio Processing
    
    /// Upload and process audio file
    /// - Parameter audioURL: Local file URL of the recorded audio
    /// - Returns: Audio processing response with transcription and food items
    func processAudio(audioURL: URL) async throws -> AudioProcessResponse {
        let url = URL(string: "\(baseURL)/api/voice-upload")!
        
        // Create multipart form data request
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        
        let boundary = UUID().uuidString
        request.setValue("multipart/form-data; boundary=\(boundary)", forHTTPHeaderField: "Content-Type")
        
        // Read audio file data
        let audioData = try Data(contentsOf: audioURL)
        let filename = audioURL.lastPathComponent
        
        // Create multipart body
        var body = Data()
        body.append("--\(boundary)\r\n".data(using: .utf8)!)
        body.append("Content-Disposition: form-data; name=\"audio\"; filename=\"\(filename)\"\r\n".data(using: .utf8)!)
        body.append("Content-Type: audio/m4a\r\n\r\n".data(using: .utf8)!)
        body.append(audioData)
        body.append("\r\n--\(boundary)--\r\n".data(using: .utf8)!)
        
        request.httpBody = body
        
        return try await performRequest(request: request, responseType: AudioProcessResponse.self)
    }
    
    // MARK: - Entries
    
    /// Get food entries for today
    /// - Returns: Today's food entries
    func getTodayEntries() async throws -> EntriesResponse {
        let url = URL(string: "\(baseURL)/api/entries")!
        let request = URLRequest(url: url)
        
        return try await performRequest(request: request, responseType: EntriesResponse.self)
    }
    
    // MARK: - Daily Totals
    
    /// Get daily macro totals for today
    /// - Returns: Today's macro totals
    func getTodayTotals() async throws -> DailyTotalsResponse {
        let url = URL(string: "\(baseURL)/api/daily-totals")!
        let request = URLRequest(url: url)
        
        return try await performRequest(request: request, responseType: DailyTotalsResponse.self)
    }
    
    // MARK: - Entry Management
    
    /// Delete a food entry by ID
    /// - Parameter entryId: The ID of the entry to delete
    /// - Returns: Success response
    func deleteEntry(entryId: String) async throws -> APIResponse {
        let url = URL(string: "\(baseURL)/api/entries/\(entryId)")!
        var request = URLRequest(url: url)
        request.httpMethod = "DELETE"
        
        return try await performRequest(request: request, responseType: BasicResponse.self)
    }
    
    /// Update individual items within a food entry session
    /// - Parameters:
    ///   - entryId: The session ID of the entry to update
    ///   - itemUpdates: Array of item updates with food name and new quantity
    /// - Returns: Success response
    func updateEntryItems(entryId: String, itemUpdates: [[String: String]]) async throws -> APIResponse {
        let url = URL(string: "\(baseURL)/api/entries/\(entryId)/items")!
        var request = URLRequest(url: url)
        request.httpMethod = "PUT"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        
        let requestBody = ["items": itemUpdates]
        request.httpBody = try jsonEncoder.encode(requestBody)
        
        return try await performRequest(request: request, responseType: BasicResponse.self)
    }
    
    // MARK: - Weight Tracking
    
    /// Get user goals (weight target, calorie target, protein target)
    /// - Returns: Current user goals
    func getUserGoals() async throws -> UserGoalsResponse {
        let url = URL(string: "\(baseURL)/api/user-goals")!
        let request = URLRequest(url: url)
        
        return try await performRequest(request: request, responseType: UserGoalsResponse.self)
    }
    
    /// Update user goals
    /// - Parameter goals: New goals to set
    /// - Returns: Success response with updated goals
    func updateUserGoals(_ goals: [String: Any]) async throws -> UserGoalsResponse {
        let url = URL(string: "\(baseURL)/api/user-goals")!
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        
        let jsonData = try JSONSerialization.data(withJSONObject: goals)
        request.httpBody = jsonData
        
        return try await performRequest(request: request, responseType: UserGoalsResponse.self)
    }
    
    /// Add a new weight entry
    /// - Parameter weightKg: Weight in kilograms
    /// - Returns: Success response
    func addWeightEntry(weightKg: Double) async throws -> BasicResponse {
        let url = URL(string: "\(baseURL)/api/weight-entries")!
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        
        let requestBody = ["weight_kg": weightKg]
        request.httpBody = try jsonEncoder.encode(requestBody)
        
        return try await performRequest(request: request, responseType: BasicResponse.self)
    }
    
    /// Get weight entries within a date range
    /// - Parameters:
    ///   - startDate: Start date in YYYY-MM-DD format
    ///   - endDate: End date in YYYY-MM-DD format
    /// - Returns: Weight entries response
    func getWeightEntries(startDate: String? = nil, endDate: String? = nil) async throws -> WeightEntriesResponse {
        var urlComponents = URLComponents(string: "\(baseURL)/api/weight-entries")!
        var queryItems: [URLQueryItem] = []
        
        if let startDate = startDate {
            queryItems.append(URLQueryItem(name: "start_date", value: startDate))
        }
        if let endDate = endDate {
            queryItems.append(URLQueryItem(name: "end_date", value: endDate))
        }
        
        if !queryItems.isEmpty {
            urlComponents.queryItems = queryItems
        }
        
        let request = URLRequest(url: urlComponents.url!)
        return try await performRequest(request: request, responseType: WeightEntriesResponse.self)
    }
    
    /// Delete a weight entry by ID
    /// - Parameter entryId: The ID of the weight entry to delete
    /// - Returns: Success response
    func deleteWeightEntry(entryId: Int) async throws -> BasicResponse {
        let url = URL(string: "\(baseURL)/api/weight-entries/\(entryId)")!
        var request = URLRequest(url: url)
        request.httpMethod = "DELETE"
        
        return try await performRequest(request: request, responseType: BasicResponse.self)
    }
    
    /// Get weight history for chart display
    /// - Parameter period: Time period (today, week, month)
    /// - Returns: Weight history response
    func getWeightHistory(period: TimePeriod) async throws -> WeightHistoryResponse {
        let url = URL(string: "\(baseURL)/api/weight-history?period=\(period.rawValue)")!
        let request = URLRequest(url: url)
        
        return try await performRequest(request: request, responseType: WeightHistoryResponse.self)
    }
    
    /// Get calorie history for chart display  
    /// - Parameter period: Time period (today, week, month)
    /// - Returns: Calorie history response
    func getCalorieHistory(period: TimePeriod) async throws -> CalorieHistoryResponse {
        let url = URL(string: "\(baseURL)/api/calorie-history?period=\(period.rawValue)")!
        let request = URLRequest(url: url)
        
        return try await performRequest(request: request, responseType: CalorieHistoryResponse.self)
    }
    
    /// Get formatted weight chart data
    /// - Parameter period: Time period for the chart
    /// - Returns: Weight chart data ready for visualization
    func getWeightChartData(period: TimePeriod) async throws -> WeightChartData {
        do {
            let response = try await getWeightHistory(period: period)
            
            // Convert response to chart data points
            let dateFormatter = DateFormatter()
            dateFormatter.dateFormat = "yyyy-MM-dd"
            
            var chartPoints = response.data.compactMap { point -> ChartDataPoint? in
                guard let date = dateFormatter.date(from: point.date) else { return nil }
                return ChartDataPoint(
                    date: date,
                    value: point.weightKg,
                    goalValue: point.goalWeightKg
                )
            }
            
            // For month view, calculate weekly averages to reduce chart complexity
            if period == .month && chartPoints.count > 7 {
                chartPoints = calculateWeeklyAverages(from: chartPoints)
            }
            
            let goalWeight = response.data.first?.goalWeightKg
            
            return WeightChartData(
                weightPoints: chartPoints,
                goalWeight: goalWeight,
                period: period,
                isEmpty: chartPoints.isEmpty
            )
        } catch {
            // Return empty data on error
            return WeightChartData.empty
        }
    }
    
    /// Get formatted calorie chart data
    /// - Parameter period: Time period for the chart
    /// - Returns: Calorie chart data ready for visualization
    func getCalorieChartData(period: TimePeriod) async throws -> CalorieChartData {
        do {
            let response = try await getCalorieHistory(period: period)
            
            // Convert response to chart data points
            let dateFormatter = DateFormatter()
            dateFormatter.dateFormat = "yyyy-MM-dd"
            
            var chartPoints = response.data.compactMap { point -> ChartDataPoint? in
                guard let date = dateFormatter.date(from: point.date) else { return nil }
                return ChartDataPoint(
                    date: date,
                    value: Double(point.calories),
                    goalValue: Double(point.goalCalories)
                )
            }
            
            // For month view, calculate weekly averages to reduce chart complexity
            if period == .month && chartPoints.count > 7 {
                chartPoints = calculateWeeklyAverages(from: chartPoints)
            }
            
            let goalCalories = response.data.first?.goalCalories ?? 1800
            
            return CalorieChartData(
                caloriePoints: chartPoints,
                goalCalories: goalCalories,
                period: period,
                isEmpty: chartPoints.isEmpty
            )
        } catch {
            // Return empty data on error
            return CalorieChartData.empty
        }
    }
    
    // MARK: - Helper Methods
    
    /// Calculate weekly averages from daily data points for better month view visualization
    /// - Parameter dataPoints: Array of daily chart data points
    /// - Returns: Array of weekly averaged chart data points
    private func calculateWeeklyAverages(from dataPoints: [ChartDataPoint]) -> [ChartDataPoint] {
        let sortedPoints = dataPoints.sorted { $0.date < $1.date }
        guard !sortedPoints.isEmpty else { return [] }
        
        let calendar = Calendar.current
        var weeklyData: [Date: (values: [Double], goalValues: [Double?], count: Int)] = [:]
        
        // Group data by week
        for point in sortedPoints {
            let weekStart = calendar.dateInterval(of: .weekOfYear, for: point.date)?.start ?? point.date
            
            if weeklyData[weekStart] == nil {
                weeklyData[weekStart] = (values: [], goalValues: [], count: 0)
            }
            
            weeklyData[weekStart]?.values.append(point.value)
            weeklyData[weekStart]?.goalValues.append(point.goalValue)
            weeklyData[weekStart]?.count += 1
        }
        
        // Calculate averages for each week
        let weeklyAverages = weeklyData.map { (weekStart, data) -> ChartDataPoint in
            let averageValue = data.values.reduce(0, +) / Double(data.values.count)
            
            let nonNilGoalValues = data.goalValues.compactMap { $0 }
            let averageGoalValue = nonNilGoalValues.isEmpty ? nil : nonNilGoalValues.reduce(0, +) / Double(nonNilGoalValues.count)
            
            return ChartDataPoint(
                date: weekStart,
                value: averageValue,
                goalValue: averageGoalValue
            )
        }
        
        return weeklyAverages.sorted { $0.date < $1.date }
    }
    
    // MARK: - Private Methods
    
    /// Perform an HTTP request and decode the response
    /// - Parameters:
    ///   - request: The URLRequest to perform
    ///   - responseType: The expected response type
    /// - Returns: Decoded response object
    private func performRequest<T: APIResponse>(request: URLRequest, responseType: T.Type) async throws -> T {
        do {
            let (data, response) = try await urlSession.data(for: request)
            
            guard let httpResponse = response as? HTTPURLResponse else {
                throw APIError.invalidResponse
            }
            
            // Check for HTTP error status codes
            switch httpResponse.statusCode {
            case 200...299:
                // Success - decode the response
                do {
                    let decodedResponse = try jsonDecoder.decode(responseType, from: data)
                    return decodedResponse
                } catch {
                    // If decoding fails, try to decode as error response
                    if let errorResponse = try? jsonDecoder.decode(ErrorResponse.self, from: data) {
                        throw APIError.serverError(errorResponse.error)
                    } else {
                        throw APIError.decodingError(error)
                    }
                }
            case 400...499:
                // Client error - try to decode error response
                if let errorResponse = try? jsonDecoder.decode(ErrorResponse.self, from: data) {
                    throw APIError.serverError(errorResponse.error)
                } else {
                    throw APIError.httpError(httpResponse.statusCode)
                }
            case 500...599:
                // Server error
                if let errorResponse = try? jsonDecoder.decode(ErrorResponse.self, from: data) {
                    throw APIError.serverError(errorResponse.error)
                } else {
                    throw APIError.httpError(httpResponse.statusCode)
                }
            default:
                throw APIError.httpError(httpResponse.statusCode)
            }
            
        } catch let error as APIError {
            throw error
        } catch {
            throw APIError.networkError(error)
        }
    }
}

// MARK: - API Errors

/// Errors that can occur when communicating with the API
enum APIError: LocalizedError {
    case invalidResponse
    case networkError(Error)
    case httpError(Int)
    case serverError(String)
    case decodingError(Error)
    
    var errorDescription: String? {
        switch self {
        case .invalidResponse:
            return "Invalid response from server"
        case .networkError(let error):
            return "Network error: \(error.localizedDescription)"
        case .httpError(let statusCode):
            return "HTTP error: \(statusCode)"
        case .serverError(let message):
            return "Server error: \(message)"
        case .decodingError(let error):
            return "Response parsing error: \(error.localizedDescription)"
        }
    }
}