#!/usr/bin/env python3
"""
Simple test for transcription module
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from transcription import transcribe_file

def test_transcription():
    """Test transcription with sample audio file"""
    test_file = "test_data/sample_food_recording.wav"
    
    if not os.path.exists(test_file):
        print(f"❌ Test file not found: {test_file}")
        print("Please add a sample WAV file to test_data/")
        return False
    
    try:
        print(f"🎤 Testing transcription with {test_file}...")
        result = transcribe_file(test_file)
        
        if result:
            print(f"✅ Transcription successful!")
            print(f"Result: \"{result}\"")
            return True
        else:
            print("❌ Transcription failed - no result returned")
            return False
            
    except Exception as e:
        print(f"❌ Transcription failed with error: {e}")
        return False

if __name__ == "__main__":
    success = test_transcription()
    exit(0 if success else 1)