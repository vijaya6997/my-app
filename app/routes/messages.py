from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import current_user, login_required
from app import db
from app.models import User, Message
from app.utils import save_attachment

messages = Blueprint('messages', __name__)

@messages.route('/messages')
@login_required
def inbox():
    # Fetch all unique users current_user has chatted with
    sent = db.session.query(Message.receiver_id).filter_by(sender_id=current_user.id)
    received = db.session.query(Message.sender_id).filter_by(receiver_id=current_user.id)
    user_ids = sent.union(received).all()
    
    users = []
    if user_ids:
        ids = [uid[0] for uid in user_ids]
        users = User.query.filter(User.id.in_(ids)).all()
        
    return render_template('messages/inbox.html', chat_users=users)

@messages.route('/messages/<username>', methods=['GET', 'POST'])
@login_required
def chat(username):
    other_user = User.query.filter_by(username=username).first_or_404()
    if request.method == 'POST':
        body = request.form.get('body')
        file = request.files.get('attachment')
        attachment_path = save_attachment(file)
        
        if body or attachment_path:
            msg = Message(sender_id=current_user.id, receiver_id=other_user.id, 
                          body=body, attachment_path=attachment_path)
            db.session.add(msg)
            db.session.commit()
        return redirect(url_for('messages.chat', username=username))
    
    msgs = Message.query.filter(
        ((Message.sender_id == current_user.id) & (Message.receiver_id == other_user.id)) |
        ((Message.sender_id == other_user.id) & (Message.receiver_id == current_user.id))
    ).order_by(Message.timestamp.asc()).all()
    
    return render_template('messages/conversation.html', other_user=other_user, msgs=msgs)
