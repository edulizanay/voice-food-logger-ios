import SwiftUI
import Charts

/// Calorie tracking chart component displaying intake with goal comparison
struct CalorieChart: View {
    let data: CalorieChartData
    @State private var selectedPoint: ChartDataPoint?
    @State private var showTooltip: Bool = false
    
    var body: some View {
        VStack(spacing: 16) {
            if data.isEmpty {
                emptyStateView
            } else {
                chartView
            }
        }
        .frame(minHeight: 200)
    }
    
    // MARK: - Chart View
    
    private var chartView: some View {
        VStack(spacing: 12) {
            // Chart header with current stats
            chartHeader
            
            // Main chart
            Chart {
                // Calorie intake area and line
                ForEach(data.caloriePoints) { point in
                    AreaMark(
                        x: .value("Date", point.date, unit: .day),
                        y: .value("Calories", point.value)
                    )
                    .foregroundStyle(
                        LinearGradient(
                            colors: [calorieColor(for: point.value).opacity(0.3), calorieColor(for: point.value).opacity(0.1)],
                            startPoint: .top,
                            endPoint: .bottom
                        )
                    )
                    
                    LineMark(
                        x: .value("Date", point.date, unit: .day),
                        y: .value("Calories", point.value)
                    )
                    .foregroundStyle(calorieColor(for: point.value))
                    .lineStyle(StrokeStyle(lineWidth: 2))
                    
                    PointMark(
                        x: .value("Date", point.date, unit: .day),
                        y: .value("Calories", point.value)
                    )
                    .foregroundStyle(calorieColor(for: point.value))
                    .opacity(selectedPoint?.id == point.id ? 1.0 : 0.7)
                }
                
                // Goal calorie line
                RuleMark(y: .value("Goal", Double(data.goalCalories)))
                    .foregroundStyle(Color.red)
                    .lineStyle(StrokeStyle(lineWidth: 1, dash: [5, 3]))
                
                // Selection overlay
                if let selectedPoint = selectedPoint {
                    RectangleMark(
                        x: .value("Date", selectedPoint.date, unit: .day),
                        width: .ratio(0.03)
                    )
                    .foregroundStyle(calorieColor(for: selectedPoint.value).opacity(0.2))
                }
            }
            .chartAngleSelection(value: .constant(nil as Double?))
            .chartBackground { chartProxy in
                GeometryReader { geometry in
                    Rectangle()
                        .fill(Color.clear)
                        .contentShape(Rectangle())
                        .onTapGesture { location in
                            handleChartTap(location: location, geometry: geometry, chartProxy: chartProxy)
                        }
                }
            }
            .chartYAxis {
                AxisMarks(position: .leading) { value in
                    AxisValueLabel {
                        if let calories = value.as(Double.self) {
                            Text("\(Int(calories))")
                                .font(.caption)
                                .foregroundStyle(.secondary)
                        }
                    }
                    AxisGridLine(stroke: StrokeStyle(lineWidth: 0.5))
                        .foregroundStyle(Color.gray.opacity(0.3))
                }
            }
            .chartXAxis {
                AxisMarks(position: .bottom, values: .stride(by: axisStride)) { _ in
                    AxisValueLabel(format: .dateTime.month(.abbreviated).day())
                        .font(.caption)
                        .foregroundStyle(.secondary)
                }
            }
            .frame(height: 160)
            
            // Tooltip overlay
            if showTooltip, let selectedPoint = selectedPoint {
                tooltipView(for: selectedPoint)
                    .transition(.opacity)
            }
        }
        .animation(.easeInOut(duration: 0.2), value: selectedPoint)
        .animation(.easeInOut(duration: 0.2), value: showTooltip)
    }
    
    // MARK: - Chart Header
    
    private var chartHeader: some View {
        HStack {
            VStack(alignment: .leading, spacing: 4) {
                Text("Calorie Intake")
                    .font(.headline)
                    .foregroundColor(.primary)
                
                if let latestCalories = data.caloriePoints.last {
                    HStack(spacing: 8) {
                        Text("\(Int(latestCalories.value))")
                            .font(.title2)
                            .fontWeight(.semibold)
                            .foregroundColor(calorieColor(for: latestCalories.value))
                        
                        Text("cal")
                            .font(.subheadline)
                            .foregroundStyle(.secondary)
                        
                        calorieProgressIndicator(current: Int(latestCalories.value), goal: data.goalCalories)
                    }
                }
            }
            
            Spacer()
            
            // Period indicator
            Text(data.period.displayName)
                .font(.caption)
                .foregroundStyle(.secondary)
                .padding(.horizontal, 8)
                .padding(.vertical, 4)
                .background(Color.gray.opacity(0.1))
                .cornerRadius(6)
        }
    }
    
    // MARK: - Calorie Color Logic
    
    private func calorieColor(for calories: Double) -> Color {
        let percentage = calories / Double(data.goalCalories)
        
        if percentage <= 0.8 {
            return .green  // Under goal - good
        } else if percentage <= 1.1 {
            return .orange  // Near goal - moderate
        } else {
            return .red  // Over goal - warning
        }
    }
    
    // MARK: - Calorie Progress Indicator
    
    private func calorieProgressIndicator(current: Int, goal: Int) -> some View {
        let remaining = goal - current
        let percentage = Double(current) / Double(goal)
        
        return HStack(spacing: 4) {
            if remaining > 0 {
                Image(systemName: "arrow.down")
                    .font(.caption)
                    .foregroundColor(.green)
                Text("\(remaining) left")
                    .font(.caption)
                    .foregroundStyle(.secondary)
            } else if remaining == 0 {
                Image(systemName: "target")
                    .font(.caption)
                    .foregroundColor(.green)
                Text("Goal met!")
                    .font(.caption)
                    .foregroundColor(.green)
            } else {
                Image(systemName: "exclamationmark.triangle")
                    .font(.caption)
                    .foregroundColor(.red)
                Text("\(abs(remaining)) over")
                    .font(.caption)
                    .foregroundColor(.red)
            }
        }
    }
    
    // MARK: - Empty State
    
    private var emptyStateView: some View {
        VStack(spacing: 16) {
            Image(systemName: "chart.bar.fill")
                .font(.largeTitle)
                .foregroundColor(.gray)
            
            Text("No Calorie Data")
                .font(.headline)
                .foregroundColor(.primary)
            
            Text("Start logging food to see your calorie intake")
                .font(.subheadline)
                .foregroundStyle(.secondary)
                .multilineTextAlignment(.center)
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .background(Color.gray.opacity(0.05))
        .cornerRadius(12)
    }
    
    // MARK: - Tooltip
    
    private func tooltipView(for point: ChartDataPoint) -> some View {
        VStack(spacing: 6) {
            Text(point.date, format: .dateTime.weekday(.wide).month().day())
                .font(.caption)
                .foregroundStyle(.secondary)
            
            HStack(spacing: 16) {
                VStack(alignment: .leading, spacing: 2) {
                    Text("Intake")
                        .font(.caption2)
                        .foregroundStyle(.secondary)
                    HStack(spacing: 4) {
                        Text("\(Int(point.value))")
                            .font(.subheadline)
                            .fontWeight(.medium)
                            .foregroundColor(calorieColor(for: point.value))
                        Text("cal")
                            .font(.caption)
                            .foregroundStyle(.secondary)
                    }
                }
                
                if let goalValue = point.goalValue {
                    VStack(alignment: .leading, spacing: 2) {
                        Text("Goal")
                            .font(.caption2)
                            .foregroundStyle(.secondary)
                        HStack(spacing: 4) {
                            Text("\(Int(goalValue))")
                                .font(.subheadline)
                                .fontWeight(.medium)
                                .foregroundColor(.red)
                            Text("cal")
                                .font(.caption)
                                .foregroundStyle(.secondary)
                        }
                    }
                }
                
                // Progress percentage
                VStack(alignment: .leading, spacing: 2) {
                    Text("Progress")
                        .font(.caption2)
                        .foregroundStyle(.secondary)
                    let percentage = (point.goalValue != nil) ? (point.value / point.goalValue! * 100) : 0
                    Text("\(Int(percentage))%")
                        .font(.subheadline)
                        .fontWeight(.medium)
                        .foregroundColor(.primary)
                }
            }
        }
        .padding(.horizontal, 12)
        .padding(.vertical, 8)
        .background(Color(UIColor.systemBackground))
        .cornerRadius(8)
        .shadow(radius: 4)
        .overlay(
            RoundedRectangle(cornerRadius: 8)
                .stroke(Color.gray.opacity(0.2), lineWidth: 1)
        )
    }
    
    // MARK: - Helper Methods
    
    private var axisStride: Calendar.Component {
        switch data.period {
        case .today:
            return .hour
        case .week:
            return .day
        case .month:
            return .weekOfYear
        }
    }
    
    private func handleChartTap(location: CGPoint, geometry: GeometryProxy, chartProxy: ChartProxy) {
        // Find the closest data point to the tap location
        guard !data.caloriePoints.isEmpty else { return }
        
        let plotFrame = geometry.frame(in: .local)
        let datePosition = chartProxy.position(forX: location.x - plotFrame.minX)
        
        if let date = datePosition {
            let targetDate = Date(timeIntervalSince1970: date)
            
            let closestPoint = data.caloriePoints.min { point1, point2 in
                abs(point1.date.timeIntervalSince(targetDate)) < abs(point2.date.timeIntervalSince(targetDate))
            }
            
            if let point = closestPoint {
                selectedPoint = point
                showTooltip = true
                
                // Hide tooltip after 3 seconds
                DispatchQueue.main.asyncAfter(deadline: .now() + 3) {
                    withAnimation {
                        showTooltip = false
                        selectedPoint = nil
                    }
                }
            }
        }
    }
}

// MARK: - Preview

struct CalorieChart_Previews: PreviewProvider {
    static var previews: some View {
        let sampleData = CalorieChartData(
            caloriePoints: [
                ChartDataPoint(date: Date().addingTimeInterval(-6*24*3600), value: 1650, goalValue: 1800),
                ChartDataPoint(date: Date().addingTimeInterval(-4*24*3600), value: 1920, goalValue: 1800),
                ChartDataPoint(date: Date().addingTimeInterval(-2*24*3600), value: 1720, goalValue: 1800),
                ChartDataPoint(date: Date(), value: 1580, goalValue: 1800)
            ],
            goalCalories: 1800,
            period: .week,
            isEmpty: false
        )
        
        VStack(spacing: 20) {
            CalorieChart(data: sampleData)
                .padding()
            
            CalorieChart(data: CalorieChartData.empty)
                .padding()
        }
        .previewLayout(.sizeThatFits)
    }
}