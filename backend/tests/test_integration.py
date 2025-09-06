#!/usr/bin/env python3
"""
Simple integration test for the complete pipeline
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from transcription import transcribe_file
from processing import process_food_text
from storage import store_food_data, get_today_entries

def test_integration():
    """Test the complete pipeline integration"""
    test_audio = "test_data/sample_food_recording.wav"
    
    print("🔗 Testing complete pipeline integration...")
    
    # Test 1: Check if test audio exists
    if not os.path.exists(test_audio):
        print(f"❌ Test audio file not found: {test_audio}")
        print("Please add a sample WAV file to test the complete pipeline")
        return False
    
    try:
        # Step 1: Test transcription
        print(f"\nStep 1: Transcribing {test_audio}...")
        transcription = transcribe_file(test_audio)
        if not transcription:
            print("❌ Transcription failed")
            return False
        print(f"✅ Transcription: \"{transcription}\"")
        
        # Step 2: Test processing
        print(f"\nStep 2: Processing food text...")
        parsed_data = process_food_text(transcription)
        if not parsed_data or 'items' not in parsed_data:
            print("❌ Processing failed")
            return False
        print(f"✅ Found {len(parsed_data['items'])} food items")
        
        # Step 3: Test storage
        print(f"\nStep 3: Storing data...")
        success = store_food_data(parsed_data['items'])
        if not success:
            print("❌ Storage failed")
            return False
        print("✅ Data stored successfully")
        
        # Step 4: Verify retrieval
        print(f"\nStep 4: Verifying data retrieval...")
        entries = get_today_entries()
        if not entries:
            print("❌ No entries found")
            return False
        
        print(f"✅ Retrieved {len(entries)} entries")
        print(f"\n🎉 Complete pipeline test passed!")
        print(f"\nFinal result:")
        for entry in entries[-1:]:
            print(f"  Timestamp: {entry['timestamp']}")
            for item in entry['items']:
                print(f"  - {item['food']}: {item['quantity']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Pipeline test failed with error: {e}")
        return False

if __name__ == "__main__":
    success = test_integration()
    exit(0 if success else 1)