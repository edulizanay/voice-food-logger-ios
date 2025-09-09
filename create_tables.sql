-- Create food_entries table for Voice Food Logger
CREATE TABLE IF NOT EXISTS food_entries (
  id BIGSERIAL PRIMARY KEY,
  food_name TEXT NOT NULL,
  quantity TEXT NOT NULL,
  calories NUMERIC(8,2),
  protein NUMERIC(8,2),
  carbs NUMERIC(8,2),
  fat NUMERIC(8,2),
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create index for fast date-based queries
CREATE INDEX IF NOT EXISTS idx_food_entries_date ON food_entries(DATE(created_at));

-- Insert a test entry to verify the table works
INSERT INTO food_entries (food_name, quantity, calories, protein, carbs, fat) 
VALUES ('Test Entry', '100g', 200.0, 25.0, 10.0, 8.0);