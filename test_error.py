from app import create_app
import traceback

app = create_app()
app.config['TESTING'] = True
app.config['PROPAGATE_EXCEPTIONS'] = True

with app.test_client() as client:
    # Step 1: Login
    r = client.post('/login', data={
        'email': 'admin@example.com',
        'password': 'admin123'
    }, follow_redirects=False)
    print("LOGIN:", r.status_code, r.headers.get('Location'))

    # Step 2: Try each key route
    for route in ['/', '/dashboard', '/jobs', '/login', '/register']:
        try:
            r = client.get(route, follow_redirects=True)
            status = r.status_code
            print(f"GET {route}: {status}")
            if status == 500:
                text = r.data.decode('utf-8')
                print("--- 500 BODY ---")
                print(text[:3000])
                print("--- END ---")
        except Exception as e:
            print(f"GET {route}: EXCEPTION")
            traceback.print_exc()
