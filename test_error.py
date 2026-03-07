from app import create_app, db
from app.models import User

app = create_app()
with app.app_context():
    # Re-add the users that existed before (seshu, ram, sk71)
    # Only add if they don't already exist

    users_to_add = [
        {'username': 'seshu', 'email': 'seshu@gmail.com', 'password': 'seshu123', 'is_admin': True},
        {'username': 'ram', 'email': 'ram@gmail.com', 'password': 'ram123', 'is_admin': False},
        {'username': 'sk71', 'email': 'sk@gmail.com', 'password': 'sk123', 'is_admin': False},
    ]

    for u_data in users_to_add:
        existing = User.query.filter_by(email=u_data['email']).first()
        if not existing:
            user = User(
                username=u_data['username'],
                email=u_data['email'],
                is_admin=u_data['is_admin']
            )
            user.set_password(u_data['password'])
            db.session.add(user)
            print(f"Added: {u_data['email']}")
        else:
            print(f"Already exists: {u_data['email']}")

    db.session.commit()

    print("\n--- All users now in DB ---")
    for u in User.query.all():
        print(f"  {u.username} | {u.email} | admin={u.is_admin}")
