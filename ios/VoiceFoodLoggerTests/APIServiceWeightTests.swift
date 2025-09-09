// ABOUTME: Unit tests for APIService weight tracking functionality
// ABOUTME: Tests weight entry creation, retrieval, and chart data generation

import XCTest
@testable import VoiceFoodLogger

final class APIServiceWeightTests: XCTestCase {
    
    var apiService: APIService!
    
    override func setUp() {
        super.setUp()
        apiService = APIService()
    }
    
    override func tearDown() {
        apiService = nil
        super.tearDown()
    }
    
    // MARK: - Weight Entry Tests
    
    func testAddWeightEntrySuccess() async {
        let expectation = expectation(description: "Add weight entry")
        
        do {
            let response = try await apiService.addWeightEntry(weightKg: 72.5)
            XCTAssertTrue(response.success)
            XCTAssertNotNil(response.message)
            expectation.fulfill()
        } catch {
            XCTFail("Expected successful weight entry addition, but failed with error: \(error)")
        }
        
        await fulfillment(of: [expectation], timeout: 10.0)
    }
    
    func testAddWeightEntryInvalidWeight() async {
        let expectation = expectation(description: "Add invalid weight entry")
        
        do {
            _ = try await apiService.addWeightEntry(weightKg: -10.0)
            XCTFail("Expected failure for negative weight")
        } catch {
            // Expected to fail with invalid weight
            XCTAssertTrue(true, "Correctly failed with invalid weight")
            expectation.fulfill()
        }
        
        await fulfillment(of: [expectation], timeout: 10.0)
    }
    
    func testGetWeightEntriesSuccess() async {
        let expectation = expectation(description: "Get weight entries")
        
        do {
            let response = try await apiService.getWeightEntries()
            XCTAssertTrue(response.success)
            XCTAssertNotNil(response.data)
            XCTAssertTrue(response.data.count >= 0)
            
            // Verify each entry has required fields
            for entry in response.data {
                XCTAssertGreaterThan(entry.id, 0)
                XCTAssertGreaterThan(entry.weightKg, 0)
                XCTAssertNotNil(entry.createdAt)
            }
            
            expectation.fulfill()
        } catch {
            XCTFail("Expected successful weight entries retrieval, but failed with error: \(error)")
        }
        
        await fulfillment(of: [expectation], timeout: 10.0)
    }
    
    // MARK: - User Goals Tests
    
    func testGetUserGoalsSuccess() async {
        let expectation = expectation(description: "Get user goals")
        
        do {
            let response = try await apiService.getUserGoals()
            XCTAssertTrue(response.success)
            XCTAssertNotNil(response.data)
            XCTAssertGreaterThan(response.data.calorieGoal, 0)
            XCTAssertGreaterThan(response.data.weightGoalKg, 0)
            expectation.fulfill()
        } catch {
            XCTFail("Expected successful user goals retrieval, but failed with error: \(error)")
        }
        
        await fulfillment(of: [expectation], timeout: 10.0)
    }
    
    func testUpdateUserGoalsSuccess() async {
        let expectation = expectation(description: "Update user goals")
        let newGoals = UserGoals(calorieGoal: 2000, weightGoalKg: 68.0)
        
        do {
            let response = try await apiService.updateUserGoals(goals: newGoals)
            XCTAssertTrue(response.success)
            XCTAssertNotNil(response.message)
            expectation.fulfill()
        } catch {
            XCTFail("Expected successful user goals update, but failed with error: \(error)")
        }
        
        await fulfillment(of: [expectation], timeout: 10.0)
    }
    
    // MARK: - Chart Data Tests
    
    func testGetWeightChartDataSuccess() async {
        let expectation = expectation(description: "Get weight chart data")
        
        do {
            let chartData = try await apiService.getWeightChartData(period: .week)
            
            // Verify chart data structure
            XCTAssertNotNil(chartData.weightPoints)
            XCTAssertEqual(chartData.period, .week)
            
            // If data exists, verify structure
            if !chartData.weightPoints.isEmpty {
                for point in chartData.weightPoints {
                    XCTAssertNotNil(point.date)
                    XCTAssertGreaterThan(point.value, 0)
                    XCTAssertNotNil(point.id)
                }
            }
            
            expectation.fulfill()
        } catch {
            XCTFail("Expected successful weight chart data retrieval, but failed with error: \(error)")
        }
        
        await fulfillment(of: [expectation], timeout: 10.0)
    }
    
    func testGetCalorieChartDataSuccess() async {
        let expectation = expectation(description: "Get calorie chart data")
        
        do {
            let chartData = try await apiService.getCalorieChartData(period: .week)
            
            // Verify chart data structure
            XCTAssertNotNil(chartData.caloriePoints)
            XCTAssertEqual(chartData.period, .week)
            XCTAssertGreaterThan(chartData.goalCalories, 0)
            
            // If data exists, verify structure
            if !chartData.caloriePoints.isEmpty {
                for point in chartData.caloriePoints {
                    XCTAssertNotNil(point.date)
                    XCTAssertGreaterThanOrEqual(point.value, 0)
                    XCTAssertNotNil(point.id)
                }
            }
            
            expectation.fulfill()
        } catch {
            XCTFail("Expected successful calorie chart data retrieval, but failed with error: \(error)")
        }
        
        await fulfillment(of: [expectation], timeout: 10.0)
    }
    
    func testChartDataForDifferentPeriods() async {
        let periods: [TimePeriod] = [.today, .week, .month]
        let expectations = periods.map { expectation(description: "Chart data for \($0.displayName)") }
        
        for (index, period) in periods.enumerated() {
            do {
                let weightData = try await apiService.getWeightChartData(period: period)
                XCTAssertEqual(weightData.period, period)
                
                let calorieData = try await apiService.getCalorieChartData(period: period)
                XCTAssertEqual(calorieData.period, period)
                
                expectations[index].fulfill()
            } catch {
                XCTFail("Failed to get chart data for period \(period.displayName): \(error)")
            }
        }
        
        await fulfillment(of: expectations, timeout: 15.0)
    }
    
    // MARK: - Integration Tests
    
    func testCompleteWeightTrackingFlow() async {
        let expectation = expectation(description: "Complete weight tracking flow")
        
        do {
            // 1. Add a weight entry
            let addResponse = try await apiService.addWeightEntry(weightKg: 73.2)
            XCTAssertTrue(addResponse.success)
            
            // Small delay to ensure data is saved
            try await Task.sleep(nanoseconds: 500_000_000) // 0.5 seconds
            
            // 2. Retrieve entries to verify it was added
            let entriesResponse = try await apiService.getWeightEntries()
            XCTAssertTrue(entriesResponse.success)
            XCTAssertFalse(entriesResponse.data.isEmpty)
            
            // 3. Get chart data to verify it includes the new entry
            let chartData = try await apiService.getWeightChartData(period: .week)
            XCTAssertFalse(chartData.isEmpty)
            
            expectation.fulfill()
        } catch {
            XCTFail("Complete weight tracking flow failed with error: \(error)")
        }
        
        await fulfillment(of: [expectation], timeout: 15.0)
    }
}