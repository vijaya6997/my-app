import razorpay
import os
from dotenv import load_dotenv

load_dotenv()

key_id = os.environ.get('RAZORPAY_KEY_ID', 'rzp_test_YourKey')
key_secret = os.environ.get('RAZORPAY_KEY_SECRET', 'YourSecret')

client = razorpay.Client(auth=(key_id, key_secret))

# Prepare dummy data
data = {
    "type": "upi_qr",
    "name": "Test QR",
    "usage": "single_use",
    "fixed_amount": True,
    "payment_amount": 10000, # 100.00
    "description": "Test QR Code",
    "notes": {
        "test": "true"
    }
}

try:
    print("Attempting to create QR code...")
    # Try qrcode (as seen in dir output)
    qr = client.qrcode.create(data=data)
    print("Success!")
    print(qr)
except Exception as e:
    print(f"FAILED: {e}")
    import traceback
    traceback.print_exc()
