import os
from app import create_app, db
from app.utils.seed_data import seed_database

app = create_app('development')

with app.app_context():
    db.create_all()
    seed_database()
    print("Database tables created and seeded successfully.")
