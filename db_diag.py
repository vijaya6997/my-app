import os
from app import create_app, db
from app.models import User, Job

app = create_app()
with app.app_context():
    try:
        print(f"Current Instance Path: {app.instance_path}")
        print(f"DB URI: {app.config['SQLALCHEMY_DATABASE_URI']}")
        
        users = User.query.all()
        print(f"Total Users: {len(users)}")
        for u in users:
            print(f" - {u.username} ({u.email})")
            
        jobs = Job.query.all()
        print(f"Total Jobs: {len(jobs)}")
        
    except Exception as e:
        import traceback
        print("DATABASE ERROR DETECTED:")
        traceback.print_exc()
