from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import current_user, login_required
from app import db
from app.models import User, Job, Application, Notification
from app.utils import save_attachment

jobs = Blueprint('jobs', __name__)

@jobs.route('/jobs')
def list_jobs():
    search = request.args.get('search')
    if search:
        all_jobs = Job.query.filter((Job.title.contains(search) | Job.description.contains(search)) & (Job.status == 'open')).all()
    else:
        all_jobs = Job.query.filter_by(status='open').all()
    return render_template('jobs/jobs.html', jobs=all_jobs)

@jobs.route('/jobs/new', methods=['GET', 'POST'])
@login_required
def post_job():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        budget = request.form.get('budget')
        file = request.files.get('attachment')
        attachment_path = save_attachment(file)
        
        job = Job(title=title, description=description, budget=budget, 
                  poster_id=current_user.id, attachment_path=attachment_path)
        db.session.add(job)
        db.session.commit()
        flash('Job posted successfully!', 'success')
        return redirect(url_for('jobs.list_jobs'))
    return render_template('jobs/post_job.html')

@jobs.route('/jobs/<int:job_id>')
def job_detail(job_id):
    job = Job.query.get_or_404(job_id)
    return render_template('jobs/job_detail.html', job=job)

@jobs.route('/jobs/<int:job_id>/apply', methods=['POST'])
@login_required
def apply_job(job_id):
    job = Job.query.get_or_404(job_id)
    
    if job.status != 'open' or (job.applications and len(job.applications) > 0):
        flash('This job is no longer accepting applications (already has an applicant).', 'warning')
        return redirect(url_for('jobs.job_detail', job_id=job_id))

    if job.poster_id == current_user.id:
        flash('You cannot apply to your own job.', 'danger')
        return redirect(url_for('jobs.job_detail', job_id=job_id))
    
    existing_app = Application.query.filter_by(job_id=job_id, applicant_id=current_user.id).first()
    if existing_app:
        flash('You have already applied for this job.', 'warning')
        return redirect(url_for('jobs.job_detail', job_id=job_id))
    
    cover_letter = request.form.get('cover_letter')
    file = request.files.get('attachment')
    attachment_path = save_attachment(file)
    
    app = Application(job_id=job_id, applicant_id=current_user.id, 
                      cover_letter=cover_letter, attachment_path=attachment_path)
    db.session.add(app)
    
    # Create notification for job poster
    note = Notification(user_id=job.poster_id, 
                        message=f"New application for '{job.title}' from {current_user.username}",
                        link=url_for('jobs.job_detail', job_id=job.id))
    db.session.add(note)
    
    db.session.commit()
    flash('Application submitted!', 'success')
    return redirect(url_for('jobs.job_detail', job_id=job_id))

@jobs.route('/applications/<int:app_id>/accept', methods=['POST'])
@login_required
def accept_application(app_id):
    application = Application.query.get_or_404(app_id)
    job = application.job
    
    if job.poster_id != current_user.id:
        flash('Unauthorized action.', 'danger')
        return redirect(url_for('jobs.job_detail', job_id=job.id))
    
    if job.status != 'open':
        flash('This job is already assigned or closed.', 'warning')
        return redirect(url_for('jobs.job_detail', job_id=job.id))
    
    # Accept this application
    application.status = 'accepted'
    
    # Reject other applications
    for other_app in job.applications:
        if other_app.id != application.id and other_app.status == 'pending':
            other_app.status = 'rejected'
            
    # Assign worker and update job status
    job.worker_id = application.applicant_id
    job.status = 'in_progress' # We use in_progress to allow work, then poster can pay to 'complete' it
    
    # Send notification to the accepted worker
    note = Notification(user_id=application.applicant_id,
                        message=f"Your application for '{job.title}' has been accepted!",
                        link=url_for('jobs.job_detail', job_id=job.id))
    db.session.add(note)
    
    db.session.commit()
    flash(f'Application accepted! {application.applicant.username} is now working on the task.', 'success')
    return redirect(url_for('jobs.job_detail', job_id=job.id))

@jobs.route('/jobs/<int:job_id>/submit', methods=['POST'])
@login_required
def submit_work(job_id):
    job = Job.query.get_or_404(job_id)
    if job.worker_id != current_user.id:
        flash('Unauthorized action.', 'danger')
        return redirect(url_for('jobs.job_detail', job_id=job.id))
    
    if job.status != 'in_progress':
        flash('You cannot submit work for this job status.', 'warning')
        return redirect(url_for('jobs.job_detail', job_id=job.id))
        
    body = request.form.get('submission_body')
    file = request.files.get('submission_attachment')
    attachment_path = save_attachment(file)
    
    job.submission_body = body
    job.submission_attachment = attachment_path
    job.status = 'submitted'
    
    # Notify poster
    note = Notification(user_id=job.poster_id,
                        message=f"Work submitted for '{job.title}' by {current_user.username}",
                        link=url_for('jobs.job_detail', job_id=job.id))
    db.session.add(note)
    db.session.commit()
    
    flash('Work submitted successfully! Waiting for client approval.', 'success')
    return redirect(url_for('jobs.job_detail', job_id=job.id))
