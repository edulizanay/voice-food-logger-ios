#!/usr/bin/env python3
"""
Setup script to create Supabase database tables for Voice Food Logger
"""

import os
import sys
from supabase import create_client, Client

# Supabase configuration
SUPABASE_URL = "https://oytfpilstrgbwnmdltzv.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im95dGZwaWxzdHJnYndubWRsdHp2Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTczODg0MDAsImV4cCI6MjA3Mjk2NDQwMH0.Wxa2fQMq9rXeOquEvkOgAOpGmJFWmtUgSmrqd0EDrVg"

def setup_database():
    """Create the food_entries table in Supabase"""
    try:
        # Initialize Supabase client
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("✅ Connected to Supabase")
        
        # Create table SQL
        create_table_sql = """
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
        """
        
        # Create index SQL
        create_index_sql = """
        CREATE INDEX IF NOT EXISTS idx_food_entries_date 
        ON food_entries(DATE(created_at));
        """
        
        # Execute table creation
        result = supabase.rpc("exec_sql", {"sql": create_table_sql})
        print("✅ food_entries table created/verified")
        
        # Execute index creation
        result = supabase.rpc("exec_sql", {"sql": create_index_sql})
        print("✅ Database index created/verified")
        
        # Test insert
        test_entry = {
            "food_name": "Test Entry - Setup Script",
            "quantity": "100g",
            "calories": 200.0,
            "protein": 25.0,
            "carbs": 10.0,
            "fat": 8.0
        }
        
        result = supabase.table("food_entries").insert(test_entry).execute()
        print("✅ Test entry inserted successfully")
        print(f"📝 Inserted entry ID: {result.data[0]['id']}")
        
        # Verify we can read back data
        entries = supabase.table("food_entries").select("*").limit(5).execute()
        print(f"✅ Database verification: Found {len(entries.data)} entries")
        
        print("\n🎉 Database setup complete!")
        print(f"🔗 View your data at: https://supabase.com/dashboard/project/oytfpilstrgbwnmdltzv/editor")
        
    except Exception as e:
        print(f"❌ Error setting up database: {e}")
        sys.exit(1)

if __name__ == "__main__":
    setup_database()