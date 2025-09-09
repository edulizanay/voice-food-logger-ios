import json
from datetime import datetime

def handler(request, context):
    """Vercel serverless function handler for health check"""
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'application/json'},
        'body': json.dumps({
            'success': True,
            'message': 'Voice Food Logger API is running',
            'timestamp': datetime.now().isoformat(),
            'version': '1.0.0'
        })
    }