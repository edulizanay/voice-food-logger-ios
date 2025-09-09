# VoiceFoodLogger - Weight & Calorie Tracking Implementation

## 📱 APPROVED UX/UI DESIGN REFERENCE

### Status: ✅ **APPROVED** - Ready for Development

### **Navigation Experience**
- **From Dashboard**: Swipe left to reveal analytics screen
- **Visual Cue**: Small dots at bottom (•○) indicating pages + subtle left arrow hint on first launch
- **Transition**: Smooth slide animation (iOS native PageTabView feel)
- **Return**: Swipe right or tap left dot to return to dashboard

---

### **Analytics Screen Layout**

#### **Header Section** (Compact)
```
[◀ Today] [This Week] [This Month]
```
- Segmented control for time periods
- Current period highlighted
- Clean, minimal typography

#### **Weight Chart** (Top Half)
```
┌─ Weight Progress ────────────────┐
│                                  │
│  72 kg ●─────────────────────    │ ← Current weight (bold)
│      ╱                           │
│  70 kg ╱ ┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈   │ ← Goal weight (dashed line)
│     ╱                            │
│  68 kg                           │
│                                  │
│  Sep 1    Sep 15    Sep 30       │
└──────────────────────────────────┘
                                [+] ← Small weight input button
```

**Visual Details:**
- **Current Weight Line**: Solid blue line with dots at data points
- **Goal Weight Line**: Subtle gray dashed horizontal line
- **Current Point**: Larger dot with subtle glow/shadow
- **Y-Axis**: Weight values (auto-scale based on data range)
- **X-Axis**: Dates (adaptive: hours/days/weeks based on period)
- **Background**: Clean white/light gray with minimal grid lines

#### **Calorie Chart** (Bottom Half)
```
┌─ Calorie Intake ─────────────────┐
│                                  │
│ 2000 ┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈ │ ← Goal line (red dashed)
│                  ●               │
│ 1500     ●──●──●   ●─●           │ ← Actual intake (green line)
│         ╱              ╲         │
│ 1000   ╱                ╲        │
│                                  │
│  Sep 1    Sep 15    Sep 30       │
└──────────────────────────────────┘
```

**Visual Details:**
- **Actual Calories**: Solid green line with area fill (subtle alpha)
- **Goal Line**: Horizontal red dashed line at target calories
- **Color Logic**: Green when under goal, orange when close, red when over
- **Data Points**: Small dots, larger on tap for exact values

---

### **Interaction Design**

#### **Weight Input Flow**
1. **Tap [+] Button** → Slide up modal sheet
2. **Modal Content**:
   ```
   ┌─ Log Today's Weight ─┐
   │                      │
   │     [  72.5  ] kg    │ ← Large number input
   │                      │
   │ Last: 72.1 kg (+0.4) │ ← Trend indicator
   │                      │
   │ [Cancel]   [Save]    │
   └──────────────────────┘
   ```
3. **Save** → Modal dismisses, chart updates with animation
4. **Haptic Feedback** on successful save

#### **Chart Interactions**
- **Tap Data Point**: Show tooltip with exact value and date
- **Pan Gesture**: Scrub through time (for daily view)
- **Time Period Switch**: Smooth transition between periods
- **Pull to Refresh**: Update data from server

---

### **Visual Style Guide**

#### **Colors**
- **Primary**: Blue (#007AFF) - current weight, active states
- **Secondary**: Gray (#8E8E93) - goal lines, inactive states
- **Success**: Green (#34C759) - calories under goal
- **Warning**: Orange (#FF9500) - calories near goal
- **Danger**: Red (#FF3B30) - calories over goal
- **Background**: System background (white/dark mode adaptive)

#### **Typography**
- **Chart Titles**: 17pt, Medium weight
- **Axis Labels**: 13pt, Regular
- **Values**: 15pt, Medium (when highlighted)
- **Trends**: 13pt, Regular with colored indicator

#### **Animations**
- **Page Transitions**: 0.3s ease-in-out
- **Chart Loading**: Stagger line drawing from left to right
- **Data Updates**: Scale up new points, fade in lines
- **Modal Present**: Standard iOS sheet animation

---

### **Responsive Behavior**

#### **Time Periods**
- **Today**: Hourly breakdown, current day
- **This Week**: Daily points, last 7 days
- **This Month**: Daily points, last 30 days

#### **Empty States**
- **No Weight Data**: "Tap + to log your first weight"
- **No Calorie Data**: Shows message with link back to food logging
- **Loading**: Skeleton animation matching chart structure

#### **Error States**
- **Network Error**: Retry button with cached data
- **Data Error**: Fallback to last known good state

### **Approved Design Decisions:**
- **Weight Units**: kg only ✅
- **Goal Setting**: Default values for now (calorie: 1800, protein: 160g, weight: 70kg) ✅
- **Data Points**: 7 days initially, every data point shown ✅
- **Time Periods**: Today/This Week/This Month (simple) ✅
- **Chart Style**: Clean minimalist ✅
- **Colors**: Subtle pastels ✅
- **Animations**: Subtle and fast ✅
- **Layout**: Equal height charts ✅

---

## 🔧 DETAILED TECHNICAL IMPLEMENTATION TO-DO LIST

### **PHASE 1: Database Infrastructure & Setup** 

#### 🗄️ **Database Tables Creation**
- [ ] **1.1** Connect to Supabase and create `weight_entries` table
  ```sql
  CREATE TABLE weight_entries (
    id SERIAL PRIMARY KEY,
    weight_kg DECIMAL(5,2) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    notes TEXT
  );
  ```

- [ ] **1.2** Create `user_goals` table with default values
  ```sql
  CREATE TABLE user_goals (
    id SERIAL PRIMARY KEY,
    calorie_goal INTEGER DEFAULT 1800,
    protein_goal DECIMAL(5,1) DEFAULT 160,
    weight_goal_kg DECIMAL(5,2) DEFAULT 70.0,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
  );
  ```

- [ ] **1.3** Insert initial default goal record
  ```sql
  INSERT INTO user_goals (calorie_goal, protein_goal, weight_goal_kg) 
  VALUES (1800, 160, 70.0);
  ```

- [ ] **1.4** Create sample weight data for development/testing
  ```sql
  INSERT INTO weight_entries (weight_kg, created_at) VALUES 
  (72.5, NOW() - INTERVAL '7 days'),
  (72.1, NOW() - INTERVAL '5 days'),
  (71.8, NOW() - INTERVAL '3 days'),
  (71.5, NOW() - INTERVAL '1 day'),
  (71.2, NOW());
  ```

---

### **PHASE 2: Backend API Development**

#### 🔌 **API Endpoint Creation**
- [ ] **2.1** Create `api/weight-entries.py`
  - `GET /api/weight-entries` - Fetch weight entries by date range
  - `POST /api/weight-entries` - Add new weight entry
  - `DELETE /api/weight-entries/{id}` - Remove weight entry by ID
  - Query parameters: `start_date`, `end_date`, `limit`

- [ ] **2.2** Create `api/weight-history.py` 
  - `GET /api/weight-history` - Weight data aggregated by time period
  - Query params: `period` (today/week/month), `start_date`, `end_date`
  - Response format: `{date: "2024-09-09", weight_kg: 71.2, goal_weight_kg: 70.0}`

- [ ] **2.3** Create `api/calorie-history.py`
  - `GET /api/calorie-history` - Calorie data aggregated by time period
  - Extend existing daily-totals logic for date ranges
  - Response format: `{date: "2024-09-09", calories: 1650, goal_calories: 1800}`

- [ ] **2.4** Create `api/user-goals.py`
  - `GET /api/user-goals` - Fetch current user goals
  - `POST /api/user-goals` - Update user goals (weight target, calorie target, protein target)

#### 📦 **Backend Storage Functions**
- [ ] **2.5** Update `shared/supabase_storage.py` with weight functions:
  - `store_weight_entry(weight_kg: float, timestamp: datetime) -> bool`
  - `get_weight_entries(start_date: str, end_date: str) -> List[Dict]`
  - `get_weight_history_by_period(period: str) -> List[Dict]`
  - `get_user_goals() -> Dict`
  - `update_user_goals(goals: Dict) -> bool`
  - `delete_weight_entry(entry_id: int) -> bool`

---

### **PHASE 3: iOS Data Models & API Integration**

#### 📊 **Swift Data Models Creation**
- [ ] **3.1** Update `ios/VoiceFoodLogger/Models.swift` with new models:
  ```swift
  struct WeightEntry: Codable, Identifiable {
      let id: Int
      let weight_kg: Double
      let created_at: String
      let notes: String?
  }
  
  struct UserGoals: Codable {
      let id: Int
      let calorie_goal: Int
      let protein_goal: Double  
      let weight_goal_kg: Double
      let created_at: String
      let updated_at: String
  }
  ```

- [ ] **3.2** Create `ios/VoiceFoodLogger/ChartModels.swift`:
  ```swift
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
  
  struct ChartDataPoint: Identifiable {
      let id = UUID()
      let date: Date
      let value: Double
      let goalValue: Double?
  }
  
  struct WeightChartData {
      let weightPoints: [ChartDataPoint]
      let goalWeight: Double?
      let period: TimePeriod
      let isEmpty: Bool
      
      static var empty: WeightChartData {
          WeightChartData(weightPoints: [], goalWeight: nil, period: .week, isEmpty: true)
      }
  }
  
  struct CalorieChartData {
      let caloriePoints: [ChartDataPoint]
      let goalCalories: Int
      let period: TimePeriod
      let isEmpty: Bool
      
      static var empty: CalorieChartData {
          CalorieChartData(caloriePoints: [], goalCalories: 1800, period: .week, isEmpty: true)
      }
  }
  ```

#### 🌐 **API Service Extensions**
- [ ] **3.3** Update `ios/VoiceFoodLogger/APIService.swift` with weight/chart methods:
  ```swift
  // Weight entry methods
  func getWeightEntries(startDate: String, endDate: String) async throws -> [WeightEntry]
  func addWeightEntry(weight: Double) async throws -> Bool
  func deleteWeightEntry(id: Int) async throws -> Bool
  
  // Goals methods  
  func getUserGoals() async throws -> UserGoals
  func updateUserGoals(_ goals: UserGoals) async throws -> Bool
  
  // Chart data methods
  func getWeightHistory(period: TimePeriod) async throws -> [ChartDataPoint]
  func getCalorieHistory(period: TimePeriod) async throws -> [ChartDataPoint]
  func getWeightChartData(period: TimePeriod) async throws -> WeightChartData
  func getCalorieChartData(period: TimePeriod) async throws -> CalorieChartData
  ```

---

### **PHASE 4: iOS UI Components Development**

#### 📈 **Chart Component Creation**
- [ ] **4.1** Create `ios/VoiceFoodLogger/WeightChart.swift`:
  ```swift
  struct WeightChart: View {
      let data: WeightChartData
      @State private var selectedPoint: ChartDataPoint?
      @State private var showTooltip: Bool = false
      
      var body: some View {
          // Swift Charts implementation
          // - LineMark for current weight (solid blue)
          // - RuleMark for goal weight (dashed gray)
          // - PointMark for data points with tap interaction
          // - Animations for data loading
          // - Empty state handling
      }
  }
  ```

- [ ] **4.2** Create `ios/VoiceFoodLogger/CalorieChart.swift`:
  ```swift
  struct CalorieChart: View {
      let data: CalorieChartData
      @State private var selectedPoint: ChartDataPoint?
      @State private var showTooltip: Bool = false
      
      var body: some View {
          // Swift Charts implementation
          // - LineMark + AreaMark for calorie intake (green fill)
          // - RuleMark for goal calories (red dashed)
          // - Color logic: green/orange/red based on goal comparison
          // - Interactive tooltips on tap
          // - Smooth transitions between periods
      }
  }
  ```

- [ ] **4.3** Create `ios/VoiceFoodLogger/TimePeriodPicker.swift`:
  ```swift
  struct TimePeriodPicker: View {
      @Binding var selectedPeriod: TimePeriod
      
      var body: some View {
          // Segmented control using Picker
          // - Custom styling to match design
          // - Smooth selection animations
          // - Haptic feedback on selection
      }
  }
  ```

#### 🎛️ **Input & Interaction Components**
- [ ] **4.4** Create `ios/VoiceFoodLogger/WeightInputSheet.swift`:
  ```swift
  struct WeightInputSheet: View {
      @Binding var isPresented: Bool
      @State private var weightInput: String = ""
      @State private var isLoading: Bool = false
      @State private var lastWeight: Double?
      let onWeightSaved: () -> Void
      
      var body: some View {
          // Modal sheet with:
          // - Large number input field (decimal keyboard)
          // - Last weight display with trend indicator
          // - Input validation (reasonable weight ranges)
          // - Save/Cancel buttons with loading states
          // - Haptic feedback on save success
      }
  }
  ```

- [ ] **4.5** Create `ios/VoiceFoodLogger/PageIndicator.swift`:
  ```swift
  struct PageIndicator: View {
      @Binding var currentPage: Int
      let pageCount: Int
      @State private var showHint: Bool = false
      
      var body: some View {
          // Bottom page dots indicator
          // - Animated dots showing current page
          // - Tap to navigate between pages
          // - First-launch hint animation (left arrow)
          // - Auto-hide hint after 3 seconds or swipe
      }
  }
  ```

#### 🏠 **Main Analytics Screen**
- [ ] **4.6** Create `ios/VoiceFoodLogger/ChartsView.swift`:
  ```swift
  struct ChartsView: View {
      @StateObject private var apiService = APIService()
      @State private var weightData: WeightChartData = .empty
      @State private var calorieData: CalorieChartData = .empty
      @State private var selectedPeriod: TimePeriod = .week
      @State private var showingWeightInput = false
      @State private var isLoading = false
      @State private var loadingError: String?
      
      var body: some View {
          VStack(spacing: 20) {
              // Header with time period picker
              TimePeriodPicker(selectedPeriod: $selectedPeriod)
                  .padding(.horizontal)
              
              // Weight chart (top half)
              VStack {
                  HStack {
                      Text("Weight Progress")
                          .font(.headline)
                      Spacer()
                      Button(action: { showingWeightInput = true }) {
                          Image(systemName: "plus.circle.fill")
                              .font(.title2)
                              .foregroundColor(.blue)
                      }
                  }
                  .padding(.horizontal)
                  
                  WeightChart(data: weightData)
                      .frame(height: 200)
              }
              
              // Calorie chart (bottom half)
              VStack {
                  HStack {
                      Text("Calorie Intake")
                          .font(.headline)
                      Spacer()
                  }
                  .padding(.horizontal)
                  
                  CalorieChart(data: calorieData)
                      .frame(height: 200)
              }
              
              Spacer()
          }
          // Loading states, error handling, refresh functionality
      }
  }
  ```

---

### **PHASE 5: Navigation Integration & Dashboard Updates**

#### 📱 **Dashboard Navigation Updates**
- [ ] **5.1** Update `ios/VoiceFoodLogger/DashboardView.swift`:
  ```swift
  struct DashboardView: View {
      @State private var currentPage = 0
      @State private var showingFirstLaunchHint = false
      
      var body: some View {
          TabView(selection: $currentPage) {
              // Page 0: Existing dashboard content
              existingDashboardContent()
                  .tag(0)
              
              // Page 1: New analytics screen
              ChartsView()
                  .tag(1)
          }
          .tabViewStyle(PageTabViewStyle(indexDisplayMode: .never))
          .overlay(alignment: .bottom) {
              PageIndicator(currentPage: $currentPage, pageCount: 2)
                  .padding(.bottom, 50)
          }
          // First launch hint logic
      }
      
      private func existingDashboardContent() -> some View {
          // Move existing dashboard VStack content here
      }
  }
  ```

- [ ] **5.2** Add first-launch hint system:
  ```swift
  // Store in UserDefaults: "hasSeenChartsHint"
  // Show subtle left arrow animation on first app launch
  // Auto-dismiss after 3 seconds or first swipe
  // Never show again after dismissed
  ```

---

### **PHASE 6: Data Flow & State Management**

#### 🔄 **Data Loading Implementation**
- [ ] **6.1** Implement data fetching in `ChartsView`:
  - Load weight and calorie data on `.onAppear`
  - Refresh data when `selectedPeriod` changes
  - Handle loading states with skeleton animations
  - Cache data for offline viewing using UserDefaults
  - Error handling with retry functionality

- [ ] **6.2** Implement real-time updates:
  - Refresh charts when returning from dashboard (`.onAppear`)
  - Update charts immediately after adding new weight entry
  - Sync with existing food entry data for calorie charts
  - Pull-to-refresh gesture implementation

#### 🎭 **Loading & Error States**
- [ ] **6.3** Create loading state components:
  ```swift
  struct ChartSkeletonView: View {
      // Animated skeleton matching chart structure
      // Shimmer effect for loading data points
      // Placeholder axes and labels
  }
  
  struct EmptyChartView: View {
      let type: ChartType // weight or calorie
      let onAddData: () -> Void
      
      // Empty state messages and call-to-action buttons
      // Different messages for weight vs calorie data
  }
  
  struct ErrorChartView: View {
      let error: String
      let onRetry: () -> Void
      
      // Error state with retry button
      // Network error vs data error handling
  }
  ```

---

### **PHASE 7: Polish, Animations & Testing**

#### ✨ **Animations & Transitions**
- [ ] **7.1** Implement chart animations:
  - Staggered line drawing from left to right (using `AnimatablePath`)
  - Scale up animation for new data points
  - Smooth period transition with crossfade
  - Loading skeleton shimmer animations

- [ ] **7.2** Add haptic feedback:
  - Weight entry save confirmation (success haptic)
  - Data point selection feedback (light haptic)
  - Period change feedback (selection haptic)
  - Error state notification (warning haptic)

- [ ] **7.3** Page transition polish:
  - Smooth swipe gestures between dashboard and charts
  - Page indicator animation timing
  - First-launch hint animation refinement

#### 🧪 **Testing & Validation**
- [ ] **7.4** Create test data and scenarios:
  - Generate sample weight data covering 30 days
  - Test with missing data points (gaps in timeline)
  - Test extreme values (rapid weight changes)
  - Verify chart scaling and auto-adjustment

- [ ] **7.5** Test edge cases:
  - No weight data scenarios
  - No calorie data scenarios  
  - Network failure handling
  - Large date ranges (performance)
  - Goal weight not set
  - Today view with no data

- [ ] **7.6** Performance optimization:
  - Chart rendering with 100+ data points
  - Smooth scrolling and pan gestures
  - Memory usage monitoring
  - API response caching strategy

---

### **PHASE 8: Future Architecture Setup**

#### 🎵 **Audio Trigger Foundation**
- [ ] **8.1** Create `ios/VoiceFoodLogger/AudioTriggerManager.swift`:
  ```swift
  class AudioTriggerManager: ObservableObject {
      func checkDailyGoalTriggers(macros: Macros, goals: UserGoals) {
          // Architecture for future audio triggers
          // Check protein goal + calorie target conditions
          // No active triggers yet - just foundation
      }
      
      func checkWeightProgressTriggers(currentWeight: Double, goalWeight: Double) {
          // Foundation for weight-based triggers
      }
  }
  ```

- [ ] **8.2** Document trigger scenarios:
  - Protein goal met + under calorie target = success audio
  - Weight goal progress milestones
  - Greasy meal detection integration plan
  - LLM health tagging system preparation

---

## 📋 IMPLEMENTATION PROGRESS TRACKER

### **Phase Completion Status:**
- [ ] **Phase 1**: Database Infrastructure (0/4 tasks)
- [ ] **Phase 2**: Backend API Development (0/5 tasks)
- [ ] **Phase 3**: iOS Models & API Integration (0/3 tasks)
- [ ] **Phase 4**: iOS UI Components (0/6 tasks)
- [ ] **Phase 5**: Navigation Integration (0/2 tasks)
- [ ] **Phase 6**: Data Flow & State Management (0/3 tasks)
- [ ] **Phase 7**: Polish & Testing (0/6 tasks)
- [ ] **Phase 8**: Future Architecture (0/2 tasks)

### **Overall Progress: 0/31 Total Tasks**

---

## 🎯 NEXT ACTIONS

### **Ready to Start - Phase 1.1:**
**Create Supabase database tables for weight tracking**

1. Connect to Supabase database
2. Create `weight_entries` table with proper schema
3. Create `user_goals` table with default values
4. Insert sample data for development
5. Test database connections and queries

**Estimated Time:** 1-2 hours