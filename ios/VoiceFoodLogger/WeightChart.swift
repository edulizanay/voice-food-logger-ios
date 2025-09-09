import SwiftUI
import Charts

/// Weight tracking chart component displaying weight progress with goal overlay
struct WeightChart: View {
    let data: WeightChartData
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
                // Weight data line
                ForEach(data.weightPoints) { point in
                    LineMark(
                        x: .value("Date", point.date, unit: .day),
                        y: .value("Weight", point.value)
                    )
                    .foregroundStyle(Color.blue)
                    .lineStyle(StrokeStyle(lineWidth: 2))
                    
                    PointMark(
                        x: .value("Date", point.date, unit: .day),
                        y: .value("Weight", point.value)
                    )
                    .foregroundStyle(Color.blue)
                    .opacity(selectedPoint?.id == point.id ? 1.0 : 0.7)
                }
                
                // Goal weight line (if available)
                if let goalWeight = data.goalWeight {
                    RuleMark(y: .value("Goal", goalWeight))
                        .foregroundStyle(Color.gray)
                        .lineStyle(StrokeStyle(lineWidth: 1, dash: [5, 3]))
                }
                
                // Selection overlay
                if let selectedPoint = selectedPoint {
                    RectangleMark(
                        x: .value("Date", selectedPoint.date, unit: .day),
                        width: .ratio(0.03)
                    )
                    .foregroundStyle(Color.blue.opacity(0.2))
                }
            }
            .chartAngleSelection(value: .constant(nil))
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
                AxisMarks(position: .leading) { _ in
                    AxisValueLabel()
                        .font(.caption)
                        .foregroundColor(.secondary)
                    AxisGridLine(stroke: StrokeStyle(lineWidth: 0.5))
                        .foregroundStyle(Color.gray.opacity(0.3))
                }
            }
            .chartXAxis {
                AxisMarks(position: .bottom, values: .stride(by: axisStride)) { _ in
                    AxisValueLabel(format: .dateTime.month(.abbreviated).day())
                        .font(.caption)
                        .foregroundColor(.secondary)
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
                Text("Weight Progress")
                    .font(.headline)
                    .foregroundColor(.primary)
                
                if let latestWeight = data.weightPoints.last {
                    HStack(spacing: 8) {
                        Text("\(latestWeight.value, specifier: "%.1f") kg")
                            .font(.title2)
                            .fontWeight(.semibold)
                            .foregroundColor(.blue)
                        
                        if let goalWeight = data.goalWeight {
                            weightProgressIndicator(current: latestWeight.value, goal: goalWeight)
                        }
                    }
                }
            }
            
            Spacer()
            
            // Period indicator
            Text(data.period.displayName)
                .font(.caption)
                .foregroundColor(.secondary)
                .padding(.horizontal, 8)
                .padding(.vertical, 4)
                .background(Color.gray.opacity(0.1))
                .cornerRadius(6)
        }
    }
    
    // MARK: - Weight Progress Indicator
    
    private func weightProgressIndicator(current: Double, goal: Double) -> some View {
        let difference = current - goal
        let isAtGoal = abs(difference) < 0.1
        
        return HStack(spacing: 4) {
            Image(systemName: isAtGoal ? "target" : (difference > 0 ? "arrow.up" : "arrow.down"))
                .font(.caption)
                .foregroundColor(isAtGoal ? .green : (difference > 0 ? .orange : .blue))
            
            if !isAtGoal {
                Text("\(abs(difference), specifier: "%.1f") kg")
                    .font(.caption)
                    .foregroundColor(.secondary)
            }
        }
    }
    
    // MARK: - Empty State
    
    private var emptyStateView: some View {
        VStack(spacing: 16) {
            Image(systemName: "scalemass")
                .font(.largeTitle)
                .foregroundColor(.gray)
            
            Text("No Weight Data")
                .font(.headline)
                .foregroundColor(.primary)
            
            Text("Tap the + button to log your first weight entry")
                .font(.subheadline)
                .foregroundColor(.secondary)
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
                .foregroundColor(.secondary)
            
            HStack(spacing: 12) {
                VStack(alignment: .leading, spacing: 2) {
                    Text("Weight")
                        .font(.caption2)
                        .foregroundColor(.secondary)
                    Text("\(point.value, specifier: "%.1f") kg")
                        .font(.subheadline)
                        .fontWeight(.medium)
                        .foregroundColor(.blue)
                }
                
                if let goalValue = point.goalValue {
                    VStack(alignment: .leading, spacing: 2) {
                        Text("Goal")
                            .font(.caption2)
                            .foregroundColor(.secondary)
                        Text("\(goalValue, specifier: "%.1f") kg")
                            .font(.subheadline)
                            .fontWeight(.medium)
                            .foregroundColor(.gray)
                    }
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
        guard !data.weightPoints.isEmpty else { return }
        
        let plotFrame = geometry.frame(in: .local)
        let datePosition = chartProxy.position(forX: location.x - plotFrame.minX)
        
        if let date = datePosition {
            let targetDate = Date(timeIntervalSince1970: date)
            
            let closestPoint = data.weightPoints.min { point1, point2 in
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

struct WeightChart_Previews: PreviewProvider {
    static var previews: some View {
        let sampleData = WeightChartData(
            weightPoints: [
                ChartDataPoint(date: Date().addingTimeInterval(-6*24*3600), value: 72.5, goalValue: 70.0),
                ChartDataPoint(date: Date().addingTimeInterval(-4*24*3600), value: 72.1, goalValue: 70.0),
                ChartDataPoint(date: Date().addingTimeInterval(-2*24*3600), value: 71.8, goalValue: 70.0),
                ChartDataPoint(date: Date(), value: 71.2, goalValue: 70.0)
            ],
            goalWeight: 70.0,
            period: .week,
            isEmpty: false
        )
        
        VStack(spacing: 20) {
            WeightChart(data: sampleData)
                .padding()
            
            WeightChart(data: WeightChartData.empty)
                .padding()
        }
        .previewLayout(.sizeThatFits)
    }
}