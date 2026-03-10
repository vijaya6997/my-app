from app import create_app, db
from app.models import User, Transaction
import os

app = create_app()
# Force SQLite if MySQL is being stubborn
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///instance/freelance.db'

with app.app_context():
    user = User.query.filter_by(username='seshu').first()
    if user:
        user.balance += 5000
        tx = Transaction(user_id=user.id, amount=5000, type='credit', description='Manual Credit for Testing')
        db.session.add(tx)
        db.session.commit()
        print(f"SUCCESS: Added 5000 to {user.username}. New Balance: {user.balance}")
    else:
        print("User 'seshu' not found.")
