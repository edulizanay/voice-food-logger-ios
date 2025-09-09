// ABOUTME: Unit tests for weight tracking data models and structures
// ABOUTME: Tests WeightEntry, UserGoals, ChartDataPoint, and related model functionality

import XCTest
@testable import VoiceFoodLogger

final class WeightTrackingModelsTests: XCTestCase {
    
    // MARK: - WeightEntry Tests
    
    func testWeightEntryCreation() {
        let testDate = Date()
        let weightEntry = WeightEntry(
            id: 1,
            weightKg: 75.5,
            createdAt: testDate
        )
        
        XCTAssertEqual(weightEntry.id, 1)
        XCTAssertEqual(weightEntry.weightKg, 75.5)
        XCTAssertEqual(weightEntry.createdAt, testDate)
    }
    
    func testWeightEntryJSONDecoding() {
        let jsonData = """
        {
            "id": 1,
            "weight_kg": 72.3,
            "created_at": "2024-01-15T10:30:00Z"
        }
        """.data(using: .utf8)!
        
        let decoder = JSONDecoder()
        decoder.keyDecodingStrategy = .convertFromSnakeCase
        decoder.dateDecodingStrategy = .iso8601
        
        XCTAssertNoThrow {
            let weightEntry = try decoder.decode(WeightEntry.self, from: jsonData)
            XCTAssertEqual(weightEntry.id, 1)
            XCTAssertEqual(weightEntry.weightKg, 72.3, accuracy: 0.01)
            XCTAssertNotNil(weightEntry.createdAt)
        }
    }
    
    // MARK: - UserGoals Tests
    
    func testUserGoalsCreation() {
        let userGoals = UserGoals(
            calorieGoal: 1800,
            weightGoalKg: 70.0
        )
        
        XCTAssertEqual(userGoals.calorieGoal, 1800)
        XCTAssertEqual(userGoals.weightGoalKg, 70.0)
    }
    
    func testUserGoalsJSONDecoding() {
        let jsonData = """
        {
            "calorie_goal": 2000,
            "weight_goal_kg": 68.5
        }
        """.data(using: .utf8)!
        
        let decoder = JSONDecoder()
        decoder.keyDecodingStrategy = .convertFromSnakeCase
        
        XCTAssertNoThrow {
            let userGoals = try decoder.decode(UserGoals.self, from: jsonData)
            XCTAssertEqual(userGoals.calorieGoal, 2000)
            XCTAssertEqual(userGoals.weightGoalKg, 68.5, accuracy: 0.01)
        }
    }
    
    // MARK: - ChartDataPoint Tests
    
    func testChartDataPointCreation() {
        let testDate = Date()
        let dataPoint = ChartDataPoint(
            date: testDate,
            value: 1750.0,
            goalValue: 1800.0
        )
        
        XCTAssertEqual(dataPoint.date, testDate)
        XCTAssertEqual(dataPoint.value, 1750.0)
        XCTAssertEqual(dataPoint.goalValue, 1800.0)
        XCTAssertNotNil(dataPoint.id)
    }
    
    func testChartDataPointWithoutGoal() {
        let testDate = Date()
        let dataPoint = ChartDataPoint(
            date: testDate,
            value: 72.5
        )
        
        XCTAssertEqual(dataPoint.date, testDate)
        XCTAssertEqual(dataPoint.value, 72.5)
        XCTAssertNil(dataPoint.goalValue)
        XCTAssertNotNil(dataPoint.id)
    }
    
    // MARK: - TimePeriod Tests
    
    func testTimePeriodDisplayNames() {
        XCTAssertEqual(TimePeriod.today.displayName, "Today")
        XCTAssertEqual(TimePeriod.week.displayName, "Week")
        XCTAssertEqual(TimePeriod.month.displayName, "Month")
    }
    
    func testTimePeriodAllCases() {
        let allPeriods = TimePeriod.allCases
        XCTAssertEqual(allPeriods.count, 3)
        XCTAssertTrue(allPeriods.contains(.today))
        XCTAssertTrue(allPeriods.contains(.week))
        XCTAssertTrue(allPeriods.contains(.month))
    }
    
    // MARK: - WeightChartData Tests
    
    func testWeightChartDataCreation() {
        let testDate = Date()
        let dataPoints = [
            ChartDataPoint(date: testDate, value: 72.5, goalValue: 70.0),
            ChartDataPoint(date: testDate.addingTimeInterval(86400), value: 72.1, goalValue: 70.0)
        ]
        
        let chartData = WeightChartData(
            weightPoints: dataPoints,
            goalWeight: 70.0,
            period: .week,
            isEmpty: false
        )
        
        XCTAssertEqual(chartData.weightPoints.count, 2)
        XCTAssertEqual(chartData.goalWeight, 70.0)
        XCTAssertEqual(chartData.period, .week)
        XCTAssertFalse(chartData.isEmpty)
    }
    
    func testWeightChartDataEmpty() {
        let emptyData = WeightChartData.empty
        
        XCTAssertTrue(emptyData.weightPoints.isEmpty)
        XCTAssertNil(emptyData.goalWeight)
        XCTAssertEqual(emptyData.period, .week)
        XCTAssertTrue(emptyData.isEmpty)
    }
    
    // MARK: - CalorieChartData Tests
    
    func testCalorieChartDataCreation() {
        let testDate = Date()
        let dataPoints = [
            ChartDataPoint(date: testDate, value: 1650.0, goalValue: 1800.0),
            ChartDataPoint(date: testDate.addingTimeInterval(86400), value: 1720.0, goalValue: 1800.0)
        ]
        
        let chartData = CalorieChartData(
            caloriePoints: dataPoints,
            goalCalories: 1800,
            period: .week,
            isEmpty: false
        )
        
        XCTAssertEqual(chartData.caloriePoints.count, 2)
        XCTAssertEqual(chartData.goalCalories, 1800)
        XCTAssertEqual(chartData.period, .week)
        XCTAssertFalse(chartData.isEmpty)
    }
    
    func testCalorieChartDataEmpty() {
        let emptyData = CalorieChartData.empty
        
        XCTAssertTrue(emptyData.caloriePoints.isEmpty)
        XCTAssertEqual(emptyData.goalCalories, 1800)
        XCTAssertEqual(emptyData.period, .week)
        XCTAssertTrue(emptyData.isEmpty)
    }
}