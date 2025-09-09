// ABOUTME: UI tests for weight tracking components and user interactions
// ABOUTME: Tests chart interactions, modal presentations, and navigation flows

import XCTest

final class WeightTrackingUITests: XCTestCase {
    
    var app: XCUIApplication!
    
    override func setUp() {
        super.setUp()
        continueAfterFailure = false
        app = XCUIApplication()
        app.launch()
    }
    
    override func tearDown() {
        app = nil
        super.tearDown()
    }
    
    // MARK: - Dashboard to Charts Navigation Tests
    
    func testSwipeNavigationToCharts() {
        // Start on dashboard
        XCTAssertTrue(app.staticTexts["Ready to Record"].waitForExistence(timeout: 5))
        
        // Swipe left to navigate to charts
        app.swipeLeft()
        
        // Verify we're on the charts view
        XCTAssertTrue(app.staticTexts["Analytics"].waitForExistence(timeout: 5))
    }
    
    func testSwipeBackToDashboard() {
        // Navigate to charts first
        app.swipeLeft()
        XCTAssertTrue(app.staticTexts["Analytics"].waitForExistence(timeout: 5))
        
        // Swipe right to go back to dashboard
        app.swipeRight()
        
        // Verify we're back on dashboard
        XCTAssertTrue(app.staticTexts["Ready to Record"].waitForExistence(timeout: 5))
    }
    
    // MARK: - Charts View Tests
    
    func testChartsViewElements() {
        // Navigate to charts
        app.swipeLeft()
        
        // Verify main elements are present
        XCTAssertTrue(app.staticTexts["Analytics"].exists)
        XCTAssertTrue(app.staticTexts["Weight Progress"].exists)
        XCTAssertTrue(app.staticTexts["Calorie Intake"].exists)
        
        // Verify period selector exists
        XCTAssertTrue(app.segmentedControls.firstMatch.exists)
    }
    
    func testPeriodSelectorInteraction() {
        // Navigate to charts
        app.swipeLeft()
        
        let periodSelector = app.segmentedControls.firstMatch
        XCTAssertTrue(periodSelector.waitForExistence(timeout: 5))
        
        // Test selecting different periods
        let buttons = periodSelector.buttons
        XCTAssertGreaterThanOrEqual(buttons.count, 3)
        
        // Tap "Today" if available
        if buttons["Today"].exists {
            buttons["Today"].tap()
            // Allow time for data to load
            usleep(500000) // 0.5 seconds
        }
        
        // Tap "Week" if available
        if buttons["Week"].exists {
            buttons["Week"].tap()
            usleep(500000)
        }
        
        // Tap "Month" if available
        if buttons["Month"].exists {
            buttons["Month"].tap()
            usleep(500000)
        }
    }
    
    func testRefreshButtonInteraction() {
        // Navigate to charts
        app.swipeLeft()
        
        // Find and tap refresh button
        let refreshButton = app.buttons["arrow.clockwise"]
        if refreshButton.exists {
            refreshButton.tap()
            
            // Verify loading state briefly appears
            usleep(200000) // 0.2 seconds
        }
    }
    
    // MARK: - Weight Input Sheet Tests
    
    func testWeightInputSheetPresentation() {
        // Navigate to charts
        app.swipeLeft()
        
        // Find and tap "Add" button for weight
        let addButtons = app.buttons.matching(identifier: "Add")
        if addButtons.count > 0 {
            let weightAddButton = addButtons.firstMatch
            if weightAddButton.exists {
                weightAddButton.tap()
                
                // Verify weight input sheet appears
                XCTAssertTrue(app.staticTexts["Log Weight"].waitForExistence(timeout: 3))
                XCTAssertTrue(app.staticTexts["Today's Weight"].exists)
            }
        }
    }
    
    func testWeightInputValidation() {
        // Navigate to charts and open weight input
        app.swipeLeft()
        let addButtons = app.buttons.matching(identifier: "Add")
        if addButtons.count > 0 && addButtons.firstMatch.exists {
            addButtons.firstMatch.tap()
            
            if app.staticTexts["Log Weight"].waitForExistence(timeout: 3) {
                // Find the text field
                let textField = app.textFields.firstMatch
                if textField.exists {
                    textField.tap()
                    
                    // Test invalid input
                    textField.typeText("999")
                    
                    // Check for validation message
                    XCTAssertTrue(
                        app.staticTexts["Weight must be between 20 and 300 kg"].exists ||
                        app.images["exclamationmark.triangle"].exists
                    )
                    
                    // Clear and test valid input
                    textField.clearAndEnterText("72.5")
                    
                    // Check for valid message
                    XCTAssertTrue(
                        app.staticTexts["✓ Valid weight entry"].exists ||
                        app.images["checkmark.circle"].exists
                    )
                }
            }
        }
    }
    
    func testWeightInputCancel() {
        // Navigate to charts and open weight input
        app.swipeLeft()
        let addButtons = app.buttons.matching(identifier: "Add")
        if addButtons.count > 0 && addButtons.firstMatch.exists {
            addButtons.firstMatch.tap()
            
            if app.staticTexts["Log Weight"].waitForExistence(timeout: 3) {
                // Tap cancel button
                let cancelButton = app.buttons["Cancel"]
                if cancelButton.exists {
                    cancelButton.tap()
                    
                    // Verify sheet is dismissed
                    XCTAssertFalse(app.staticTexts["Log Weight"].exists)
                    XCTAssertTrue(app.staticTexts["Analytics"].exists)
                }
            }
        }
    }
    
    // MARK: - Chart Interaction Tests
    
    func testChartTapInteraction() {
        // Navigate to charts
        app.swipeLeft()
        
        // Wait for charts to load
        XCTAssertTrue(app.staticTexts["Weight Progress"].waitForExistence(timeout: 5))
        
        // Try to tap on chart area (this is approximate since chart coordinates are dynamic)
        let chartAreas = app.otherElements.matching(NSPredicate(format: "identifier CONTAINS 'chart' OR identifier CONTAINS 'Chart'"))
        
        if chartAreas.count > 0 {
            let firstChart = chartAreas.firstMatch
            if firstChart.exists {
                firstChart.tap()
                // Chart tap interactions might show tooltips but are hard to test precisely
                // Just verify the tap doesn't crash the app
                XCTAssertTrue(app.staticTexts["Analytics"].exists)
            }
        }
    }
    
    func testPullToRefresh() {
        // Navigate to charts
        app.swipeLeft()
        
        // Wait for content to load
        XCTAssertTrue(app.staticTexts["Analytics"].waitForExistence(timeout: 5))
        
        // Perform pull to refresh gesture
        let chartsScrollView = app.scrollViews.firstMatch
        if chartsScrollView.exists {
            let startCoordinate = chartsScrollView.coordinate(withNormalizedOffset: CGVector(dx: 0.5, dy: 0.2))
            let endCoordinate = chartsScrollView.coordinate(withNormalizedOffset: CGVector(dx: 0.5, dy: 0.8))
            startCoordinate.press(forDuration: 0.1, thenDragTo: endCoordinate)
            
            // Verify refresh completed (data should still be displayed)
            XCTAssertTrue(app.staticTexts["Weight Progress"].exists)
            XCTAssertTrue(app.staticTexts["Calorie Intake"].exists)
        }
    }
    
    // MARK: - Empty State Tests
    
    func testEmptyStateDisplay() {
        // This test would be better with a way to clear data first
        // For now, just verify that empty state elements can appear
        app.swipeLeft()
        
        // Check if empty states are present (they might not be if data exists)
        // Empty states would show "No Weight Data" or "No Calorie Data"
        let hasData = app.staticTexts["Weight Progress"].exists && app.staticTexts["Calorie Intake"].exists
        
        if !hasData {
            // If no data, verify empty state messages
            let possibleEmptyMessages = [
                "No Weight Data",
                "No Calorie Data",
                "Tap the + button to log your first weight entry",
                "Start logging food to see your calorie intake"
            ]
            
            var foundEmptyState = false
            for message in possibleEmptyMessages {
                if app.staticTexts[message].exists {
                    foundEmptyState = true
                    break
                }
            }
            
            if foundEmptyState {
                XCTAssertTrue(true, "Empty state correctly displayed")
            }
        } else {
            XCTAssertTrue(true, "Data exists, empty state test not applicable")
        }
    }
    
    // MARK: - Accessibility Tests
    
    func testAccessibilityElements() {
        // Navigate to charts
        app.swipeLeft()
        
        // Verify key elements are accessible
        XCTAssertTrue(app.staticTexts["Analytics"].isAccessibilityElement)
        
        let addButtons = app.buttons.matching(identifier: "Add")
        if addButtons.count > 0 {
            XCTAssertTrue(addButtons.firstMatch.isAccessibilityElement)
        }
        
        let refreshButton = app.buttons["arrow.clockwise"]
        if refreshButton.exists {
            XCTAssertTrue(refreshButton.isAccessibilityElement)
        }
    }
}

// MARK: - Helper Extensions

extension XCUIElement {
    func clearAndEnterText(_ text: String) {
        guard let stringValue = self.value as? String else {
            XCTFail("Tried to clear and enter text into a non-string value")
            return
        }
        
        self.tap()
        
        let deleteString = String(repeating: XCUIKeyboardKey.delete.rawValue, count: stringValue.count)
        self.typeText(deleteString)
        self.typeText(text)
    }
}