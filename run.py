"""
Simple runner for Alex Backend
"""
import os
os.environ['FLASK_ENV'] = 'development'

from src.main import app

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    # Run without debug reloader to avoid issues
    app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)

