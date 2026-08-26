import os
from app import create_app, db
from app.utils.seed_data import seed_database

env_name = os.getenv('FLASK_ENV', 'development')
app = create_app(env_name)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        # Seed initial demo data if database is empty
        seed_database()
    
    print("=========================================================")
    print("  NEXORA ERP - Enterprise Resource Planning & Distribution")
    print("  Server running on http://127.0.0.1:5000")
    print("=========================================================")
    app.run(host='0.0.0.0', port=5000, debug=True)
