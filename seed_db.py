from app import create_app, db
from app.models import User

app = create_app()

with app.app_context():
    # Drop and recreate for migration simplicity in this dev phase
    db.drop_all()
    db.create_all()
    
    # Create Admin
    admin = User(username='admin', email='admin@example.com', is_admin=True)
    admin.set_password('admin123')
    
    # Create Regular User
    user = User(username='testuser', email='user@example.com', is_admin=False)
    user.set_password('user123')
    
    db.session.add(admin)
    db.session.add(user)
    db.session.commit()
    
    print("Database seeded with Admin and User!")
    print("Admin: admin@example.com / admin123")
    print("User: user@example.com / user123")
