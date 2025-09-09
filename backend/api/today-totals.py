import os
import sys
import json
from datetime import datetime

# Add shared directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'shared'))

from supabase_storage import get_daily_totals

def handler(request, context):
    """Vercel serverless function handler for getting today's macro totals"""
    
    try:
        totals = get_daily_totals()
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'success': True,
                'date': datetime.now().strftime('%Y-%m-%d'),
                'totals': totals
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