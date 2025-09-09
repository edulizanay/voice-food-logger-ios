#!/usr/bin/env python3

# ABOUTME: Script to create weight tracking tables in Supabase database
# ABOUTME: Sets up weight_entries and user_goals tables with sample data

import os
import sys
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add shared directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'shared'))

from supabase_storage import _get_supabase_client

def create_weight_entries_table():
    """Create the weight_entries table in Supabase"""
    try:
        supabase = _get_supabase_client()
        
        # Check if table exists first
        try:
            result = supabase.table("weight_entries").select("id").limit(1).execute()
            print("✅ weight_entries table already exists")
            return True
        except Exception:
            print("📝 weight_entries table doesn't exist, will be created via Supabase dashboard")
            print("SQL to run in Supabase SQL Editor:")
            print("""
CREATE TABLE weight_entries (
    id SERIAL PRIMARY KEY,
    weight_kg DECIMAL(5,2) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    notes TEXT
);
""")
            return False
            
    except Exception as e:
        print(f"❌ Error connecting to Supabase: {e}")
        return False

def create_user_goals_table():
    """Create the user_goals table in Supabase"""
    try:
        supabase = _get_supabase_client()
        
        # Check if table exists first
        try:
            result = supabase.table("user_goals").select("id").limit(1).execute()
            print("✅ user_goals table already exists")
            return True
        except Exception:
            print("📝 user_goals table doesn't exist, will be created via Supabase dashboard")
            print("SQL to run in Supabase SQL Editor:")
            print("""
CREATE TABLE user_goals (
    id SERIAL PRIMARY KEY,
    calorie_goal INTEGER DEFAULT 1800,
    protein_goal DECIMAL(5,1) DEFAULT 160,
    weight_goal_kg DECIMAL(5,2) DEFAULT 70.0,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
""")
            return False
            
    except Exception as e:
        print(f"❌ Error checking user_goals table: {e}")
        return False

def insert_default_goals():
    """Insert default goal values"""
    try:
        supabase = _get_supabase_client()
        
        # Check if goals already exist
        result = supabase.table("user_goals").select("*").execute()
        if result.data:
            print("✅ Default goals already exist")
            print(f"Current goals: {result.data[0]}")
            return True
        
        # Insert default goals
        goal_data = {
            "calorie_goal": 1800,
            "protein_goal": 160.0,
            "weight_goal_kg": 70.0
        }
        
        result = supabase.table("user_goals").insert(goal_data).execute()
        print("✅ Default goals inserted successfully")
        print(f"Inserted: {goal_data}")
        return True
        
    except Exception as e:
        print(f"❌ Error inserting default goals: {e}")
        print("SQL to run in Supabase SQL Editor:")
        print("""
INSERT INTO user_goals (calorie_goal, protein_goal, weight_goal_kg) 
VALUES (1800, 160, 70.0);
""")
        return False

def insert_sample_weight_data():
    """Insert sample weight data for testing"""
    try:
        supabase = _get_supabase_client()
        
        # Check if sample data already exists
        result = supabase.table("weight_entries").select("*").execute()
        if result.data:
            print(f"✅ Weight entries already exist ({len(result.data)} entries)")
            for entry in result.data[:3]:  # Show first 3
                print(f"  - {entry['created_at']}: {entry['weight_kg']} kg")
            return True
        
        # Create sample data
        now = datetime.now()
        sample_data = [
            {"weight_kg": 72.5, "created_at": (now - timedelta(days=7)).isoformat()},
            {"weight_kg": 72.1, "created_at": (now - timedelta(days=5)).isoformat()},
            {"weight_kg": 71.8, "created_at": (now - timedelta(days=3)).isoformat()},
            {"weight_kg": 71.5, "created_at": (now - timedelta(days=1)).isoformat()},
            {"weight_kg": 71.2, "created_at": now.isoformat()},
        ]
        
        result = supabase.table("weight_entries").insert(sample_data).execute()
        print("✅ Sample weight data inserted successfully")
        print(f"Inserted {len(sample_data)} weight entries")
        return True
        
    except Exception as e:
        print(f"❌ Error inserting sample data: {e}")
        print("SQL to run in Supabase SQL Editor:")
        print("""
INSERT INTO weight_entries (weight_kg, created_at) VALUES 
(72.5, NOW() - INTERVAL '7 days'),
(72.1, NOW() - INTERVAL '5 days'),
(71.8, NOW() - INTERVAL '3 days'),
(71.5, NOW() - INTERVAL '1 day'),
(71.2, NOW());
""")
        return False

def main():
    """Main setup function"""
    print("🚀 Setting up Weight Tracking Database Tables")
    print("=" * 50)
    
    # Step 1: Create weight_entries table
    print("\n📋 Step 1: Creating weight_entries table...")
    weight_table_exists = create_weight_entries_table()
    
    # Step 2: Create user_goals table  
    print("\n📋 Step 2: Creating user_goals table...")
    goals_table_exists = create_user_goals_table()
    
    if not weight_table_exists or not goals_table_exists:
        print("\n⚠️  Manual Action Required:")
        print("Some tables need to be created manually via Supabase dashboard.")
        print("Please run the SQL commands shown above in the Supabase SQL Editor,")
        print("then run this script again.")
        return
    
    # Step 3: Insert default goals
    print("\n📋 Step 3: Inserting default goals...")
    insert_default_goals()
    
    # Step 4: Insert sample weight data
    print("\n📋 Step 4: Inserting sample weight data...")
    insert_sample_weight_data()
    
    print("\n🎉 Database setup complete!")
    print("✅ Ready to proceed with backend API development")

if __name__ == "__main__":
    main()