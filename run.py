import sys
from app import create_app, db
from app.utils.seeder import seed_database
from app.services.ai_service import train_and_save_all_models

app = create_app()

if __name__ == '__main__':
    if '--seed' in sys.argv:
        with app.app_context():
            print("Initializing database...")
            db.create_all()
            print("Seeding database with sample data...")
            seed_database()
            print("Training AI models on seed data...")
            train_and_save_all_models()
            print("Seeding, database initialization, and AI model training complete.")
    else:
        app.run(debug=True, host='0.0.0.0', port=5000)
