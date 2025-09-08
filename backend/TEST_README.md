# 🧪 FitMe Backend Test Suite

Automated testing for the FitMe backend functionality, ensuring reliability and preventing regressions.

## 📋 Test Coverage

### Meal Detection Tests (`test_meal_detection.py`)
- **Breakfast Detection**: Tests 5:00 AM - 10:59 AM range
- **Lunch Detection**: Tests 11:00 AM - 2:59 PM range  
- **Dinner Detection**: Tests 6:00 PM - 9:59 PM range
- **Snack Detection**: Tests afternoon (3-6 PM) and late night/early morning periods
- **Emoji Assignment**: Verifies correct meal emojis (🌅 🥞 🌙 🍿)
- **Edge Cases**: Boundary conditions and time transitions

### Storage Tests (`test_storage.py`)
- **Data Persistence**: Verifies food entries are stored correctly
- **Meal Type Integration**: Tests automatic meal type assignment
- **Daily Totals**: Tests macro aggregation calculations
- **Multiple Entries**: Tests handling of multiple meals per day
- **File Format**: Validates JSON structure and backward compatibility
- **Empty State Handling**: Tests behavior with no data

## 🚀 Running Tests

### Quick Start
```bash
# Run all tests
python3 run_tests.py

# Run specific test file  
python3 -m unittest test_meal_detection.py
python3 -m unittest test_storage.py

# Verbose output
python3 -m unittest -v test_meal_detection.py
```

### Expected Output
```
🚀 FitMe Backend Test Suite
==============================
🧪 Running FitMe Backend Tests
==================================================

📊 Test Summary:
   ✅ Passed: 13
   ❌ Failed: 0
   💥 Errors: 0
   📈 Total: 13

🎉 All tests passed!
```

## 📁 Test Files

| File | Purpose | Tests |
|------|---------|--------|
| `test_meal_detection.py` | Meal time categorization | 7 tests |
| `test_storage.py` | Data persistence & retrieval | 6 tests |
| `run_tests.py` | Test runner with reporting | - |

## 🔧 Requirements

- **Python 3.8+**
- **Standard Library Only**: No external dependencies
- **Temporary Storage**: Tests use isolated temp directories

## 📊 Test Categories

### ✅ Unit Tests
- Individual function testing
- Input validation
- Edge case handling  
- Error condition testing

### ✅ Integration Tests
- Storage + meal detection workflow
- Multiple component interaction
- End-to-end data flow

### 📋 Test Scenarios

#### Meal Detection
- ✅ Breakfast (5:00-10:59 AM) → 🌅  
- ✅ Lunch (11:00 AM-2:59 PM) → ☀️
- ✅ Snack (3:00-5:59 PM) → 🍿
- ✅ Dinner (6:00-9:59 PM) → 🌙
- ✅ Late snack (10:00 PM-4:59 AM) → 🍿

#### Storage Operations
- ✅ Store single food entry
- ✅ Store multiple entries same day
- ✅ Calculate daily macro totals
- ✅ Handle empty data gracefully
- ✅ Backward compatibility with old format

## 🎯 Quality Metrics

- **Test Coverage**: Core functionality covered
- **Execution Time**: ~0.003 seconds
- **Reliability**: 100% pass rate
- **Isolation**: Clean test environment per run

## 🔮 Future Enhancements

- **API Endpoint Tests**: Test Flask routes  
- **Mock External Services**: Groq API simulation
- **Performance Tests**: Load testing with large datasets
- **iOS Integration Tests**: End-to-end workflow testing

---

*Run these tests before deploying changes to ensure system stability.*