from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import current_user, login_required
from app import db
from app.models import User, Job, Application, Message, Review

main = Blueprint('main', __name__)

@main.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return render_template('index.html')

@main.route('/dashboard')
@login_required
def dashboard():
    from app.models import Transaction
    jobs = Job.query.filter_by(poster_id=current_user.id).all()
    apps = Application.query.filter_by(applicant_id=current_user.id).all()
    txs = Transaction.query.filter_by(user_id=current_user.id).order_by(Transaction.timestamp.desc()).limit(10).all()
    return render_template('dashboard.html', jobs=jobs, apps=apps, transactions=txs)

@main.route('/wallet/admin_withdraw', methods=['POST'])
@login_required
def admin_withdraw():
    if not current_user.is_admin:
        flash('Unauthorized.', 'danger')
        return redirect(url_for('main.dashboard'))
        
    amount = float(request.form.get('amount', 0))
    if amount <= 0:
        flash('Invalid amount.', 'danger')
    elif current_user.platform_balance < amount:
        flash('Insufficient platform balance.', 'danger')
    else:
        current_user.platform_balance -= amount
        current_user.balance += amount
        from app.models import Transaction
        tx = Transaction(user_id=current_user.id, amount=amount, type='credit', description='Platform Admin Withdrawal to Wallet')
        db.session.add(tx)
        db.session.commit()
        flash(f'Successfully transferred ₹{amount:.2f} from the Platform Fee to your Wallet!', 'success')
        
    return redirect(url_for('main.dashboard'))

import razorpay
from flask import current_app, jsonify

@main.route('/wallet/create_order', methods=['POST'])
@login_required
def create_order():
    amount = float(request.form.get('amount', 0))
    if amount <= 0:
        return jsonify({'error': 'Invalid amount'}), 400
        
    client = razorpay.Client(auth=(current_app.config['RAZORPAY_KEY_ID'], current_app.config['RAZORPAY_KEY_SECRET']))
    
    # Razorpay amount is in paise (Multiply by 100)
    data = {"amount": int(amount * 100), "currency": "INR", "receipt": f"receipt_{current_user.id}"}
    try:
        payment = client.order.create(data=data)
        return jsonify({
            'order_id': payment['id'], 
            'amount': payment['amount'], 
            'currency': payment['currency'], 
            'key_id': current_app.config['RAZORPAY_KEY_ID']
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@main.route('/wallet/payment_success', methods=['POST'])
@login_required
def payment_success():
    razorpay_payment_id = request.form.get('razorpay_payment_id')
    razorpay_order_id = request.form.get('razorpay_order_id')
    razorpay_signature = request.form.get('razorpay_signature')
    amount_str = request.form.get('amount', '0')
    
    if not all([razorpay_payment_id, razorpay_order_id, razorpay_signature]):
        flash('Payment failed or invalid.', 'danger')
        return redirect(url_for('main.dashboard'))
        
    client = razorpay.Client(auth=(current_app.config['RAZORPAY_KEY_ID'], current_app.config['RAZORPAY_KEY_SECRET']))
    try:
        # Verify signature
        client.utility.verify_payment_signature({
            'razorpay_order_id': razorpay_order_id,
            'razorpay_payment_id': razorpay_payment_id,
            'razorpay_signature': razorpay_signature
        })
        
        amount = float(amount_str)
        current_user.balance += amount
        from app.models import Transaction # Add this line to import Transaction locally
        tx = Transaction(user_id=current_user.id, amount=amount, type='credit', description=f'Added funds (Razorpay Txn: {razorpay_payment_id})')
        db.session.add(tx)
        db.session.commit()
        flash(f'Successfully added ₹{amount:.2f} to your wallet via Razorpay!', 'success')
        
    except Exception as e:
        flash(f'Payment verification failed: {str(e)}', 'danger')
        
    return redirect(url_for('main.dashboard'))

@main.route('/wallet/generate_qr', methods=['POST'])
@login_required
def generate_qr():
    amount = float(request.form.get('amount', 0))
    if amount <= 0:
        return jsonify({'error': 'Invalid amount'}), 400
        
    key_id = current_app.config.get('RAZORPAY_KEY_ID')
    key_secret = current_app.config.get('RAZORPAY_KEY_SECRET')
    
    if not key_id or not key_secret or 'YOUR_KEY_HERE' in key_id or 'YourRazorpay' in key_id:
        return jsonify({'error': 'Razorpay API keys are not configured. Please add them to your .env file or Vercel settings.'}), 400
        
    client = razorpay.Client(auth=(key_id, key_secret))
    
    data = {
        "type": "upi_qr",
        "name": f"Wallet_{current_user.username}",
        "usage": "single_use",
        "fixed_amount": True,
        "payment_amount": int(amount * 100),
        "description": f"Add funds for {current_user.username}",
        "notes": {
            "user_id": current_user.id
        }
    }
    
    try:
        qr_code = client.qrcode.create(data=data)
        # Store QR ID in session or DB if you want to track it
        return jsonify({
            'image_url': qr_code['image_url'],
            'qr_id': qr_code['id'],
            'amount': amount
        })
    except Exception as e:
        import traceback
        return jsonify({'error': str(e), 'traceback': traceback.format_exc()}), 500

@main.route('/wallet/check_qr_status/<qr_id>')
@login_required
def check_qr_status(qr_id):
    client = razorpay.Client(auth=(current_app.config['RAZORPAY_KEY_ID'], current_app.config['RAZORPAY_KEY_SECRET']))
    try:
        payments = client.payment.all({'qr_code_id': qr_id})
        # Check if any payment associated with this QR is captured/authorized
        for payment in payments['items']:
            if payment['status'] in ['captured', 'authorized']:
                # Credit user if not already credited
                from app.models import Transaction
                # Check for existing transaction with this payment ID
                existing = Transaction.query.filter(Transaction.description.contains(payment['id'])).first()
                if not existing:
                    amount = payment['amount'] / 100
                    current_user.balance += amount
                    tx = Transaction(user_id=current_user.id, amount=amount, type='credit', description=f"Add funds (QR Code Pay: {payment['id']})")
                    db.session.add(tx)
                    db.session.commit()
                    return jsonify({'status': 'paid', 'amount': amount})
        
        return jsonify({'status': 'pending'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@main.route('/wallet/withdraw', methods=['POST'])
@login_required
def withdraw_funds():
    amount = float(request.form.get('amount', 0))
    if amount <= 0:
        flash('Invalid amount.', 'danger')
    elif current_user.balance < amount:
        flash('Insufficient balance for withdrawal.', 'danger')
    else:
        from app.models import Transaction
        
        # Calculate 5% withdrawal fee
        admin = User.query.filter_by(is_admin=True).first()
        
        if admin and current_user.id != admin.id:
            withdrawal_fee = amount * 0.05
            actual_withdrawal = amount - withdrawal_fee
            
            # Update balances
            current_user.balance -= amount
            admin.platform_balance += withdrawal_fee
            
            # Record transactions
            tx = Transaction(user_id=current_user.id, amount=amount, type='debit', 
                             description=f'Withdrawal (includes 5% fee)')
            tx_admin = Transaction(user_id=admin.id, amount=withdrawal_fee, type='credit', 
                                   description=f"5% Platform Fee from Withdrawal ({current_user.username})")
            
            db.session.add(tx)
            db.session.add(tx_admin)
            db.session.commit()
            flash(f'Successfully withdrew ₹{actual_withdrawal:.2f}! (A 5% platform fee of ₹{withdrawal_fee:.2f} was applied)', 'success')
            
        else:
            # Admins don't pay withdrawal fees
            current_user.balance -= amount
            tx = Transaction(user_id=current_user.id, amount=amount, type='debit', description='Withdrawal')
            db.session.add(tx)
            db.session.commit()
            flash(f'Successfully withdrew ₹{amount:.2f}!', 'success')
            
    return redirect(url_for('main.dashboard'))


@main.route('/jobs/<int:job_id>/pay', methods=['POST'])
@login_required
def pay_job(job_id):
    from app.models import Job, Transaction, Application, User
    job = Job.query.get_or_404(job_id)
    if job.poster_id != current_user.id:
        flash('Unauthorized action.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    if job.status != 'submitted':
        flash('Work must be submitted before payment.', 'warning')
        return redirect(url_for('jobs.job_detail', job_id=job.id))

    # Find the accepted worker to pay them
    if job.worker_id:
        seller = User.query.get(job.worker_id)
    else:
        # Fallback to the first application if none accepted (legacy support or edge case)
        application = Application.query.filter_by(job_id=job_id, status='accepted').first()
        if not application:
            application = Application.query.filter_by(job_id=job_id).first()
        
        if not application:
            flash('No workers assigned to this task.', 'warning')
            return redirect(url_for('main.dashboard'))
        seller = User.query.get(application.applicant_id)
    
    if current_user.balance < job.budget:
        flash('Insufficient balance in wallet.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    # Calculate and distribute funds
    admin = User.query.filter_by(is_admin=True).first()
    
    if admin and seller.id != admin.id:
        commission = job.budget * 0.05
        seller_earnings = job.budget - commission
        
        current_user.balance -= job.budget
        seller.balance += seller_earnings
        admin.platform_balance += commission
        
        job.status = 'completed'
        
        tx_debit = Transaction(user_id=current_user.id, amount=job.budget, type='debit', 
                               description=f"Paid {seller.username} for '{job.title}'")
        tx_credit = Transaction(user_id=seller.id, amount=seller_earnings, type='credit', 
                                description=f"Received payment for '{job.title}' (after 5% fee)")
        tx_admin = Transaction(user_id=admin.id, amount=commission, type='credit', 
                               description=f"5% Platform Fee from '{job.title}'")
        
        db.session.add(tx_debit)
        db.session.add(tx_credit)
        db.session.add(tx_admin)
    else:
        current_user.balance -= job.budget
        seller.balance += job.budget
        job.status = 'completed'
        
        tx_debit = Transaction(user_id=current_user.id, amount=job.budget, type='debit', 
                               description=f"Paid {seller.username} for '{job.title}'")
        tx_credit = Transaction(user_id=seller.id, amount=job.budget, type='credit', 
                                description=f"Received payment from {current_user.username} for '{job.title}'")
        
        db.session.add(tx_debit)
        db.session.add(tx_credit)
        
    db.session.commit()
    
    flash(f'Payment of ₹{job.budget:.2f} sent to {seller.username}!', 'success')
    return redirect(url_for('main.dashboard'))

@main.route('/profile/<username>')
def profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    reviews = Review.query.filter_by(reviewee_id=user.id).all()
    return render_template('profile/profile.html', user=user, reviews=reviews)

@main.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    if request.method == 'POST':
        current_user.bio = request.form.get('bio')
        current_user.location = request.form.get('location')
        current_user.skills = request.form.get('skills')
        db.session.commit()
        flash('Profile updated!', 'success')
        return redirect(url_for('main.profile', username=current_user.username))
    return render_template('profile/edit_profile.html')
