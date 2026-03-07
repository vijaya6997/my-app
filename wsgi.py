import os
from app import create_app, db

app = create_app()

# Auto-create tables if they don't exist (needed on first deploy)
with app.app_context():
    db.create_all()

# Vercel needs the 'app' variable exposed at module level (above handles that)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'true').lower() == 'true'
    app.run(host='0.0.0.0', port=port, debug=debug)
