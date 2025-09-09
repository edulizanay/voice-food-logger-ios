import os
import sys
import json
from datetime import datetime

# Add shared directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'shared'))

from storage import get_today_entries

def handler(request, context):
    """Vercel serverless function handler for getting today's entries"""
    
    try:
        entries = get_today_entries()
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'success': True,
                'date': datetime.now().strftime('%Y-%m-%d'),
                'entries': entries
            })
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'success': False,
                'error': str(e)
            })
        }