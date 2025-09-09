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
        let url = URL(string: "\(baseURL)/api/process-audio")!
        
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
    
    /// Update a food entry's quantity
    /// - Parameters:
    ///   - entryId: The ID of the entry to update
    ///   - newQuantity: The new quantity string (e.g., "200g")
    /// - Returns: Success response
    func updateEntry(entryId: String, newQuantity: String) async throws -> APIResponse {
        let url = URL(string: "\(baseURL)/api/entries/\(entryId)")!
        var request = URLRequest(url: url)
        request.httpMethod = "PUT"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        
        let requestBody = ["quantity": newQuantity]
        request.httpBody = try jsonEncoder.encode(requestBody)
        
        return try await performRequest(request: request, responseType: BasicResponse.self)
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