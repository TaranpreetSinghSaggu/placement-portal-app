from flask import render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from datetime import datetime

from app import app
from models import PlacementDrive, db, Company, Application, Student, Interview
from mail_utils import (
    send_application_status_update,
    send_interview_scheduled,
    send_interview_cancelled,
)

@app.route('/company/dashboard')
@login_required
def company_dash():
    company = Company.query.filter_by(id=current_user.id).first()

    if company is None:
        return redirect(url_for('login'))
    
    if company.is_approved == False:
        return "<h3>Your account is not approved yet. Please wait for admin approval.</h3>"
    
    if company.is_blacklisted == True:
        return "<h3>Your account has been blacklisted. Contact admin for more information.</h3>"
    
    drives = PlacementDrive.query.filter_by(company_id=current_user.id).all()

    total_applications = 0

    for drive in drives:
        app = Application.query.filter_by(drive_id=drive.id).all()
        total_applications = total_applications + len(app)

    return render_template("company/dashboard.html",company=company, drives=drives, total_jobs= len(drives), total_applications=total_applications)

@app.route('/company/jobs/create', methods=['GET', 'POST'])
@login_required
def job_creation():
    company = Company.query.filter_by(id=current_user.id).first()

    if company is None:
        return redirect(url_for('login'))

    if company.is_approved == False:
        return "<h3>Your account is not approved. You cannot create job postings.</h3>"
    
    if company.is_blacklisted == True:
        return "<h3>Your account is blacklisted. You cannot create job postings.</h3>"
    
    if request.method == 'POST':
        title = request.form["job_title"]
        description = request.form["job_description"]
        eligibility = request.form["eligibility"]
        deadline_str = request.form["deadline"]

        try:
            deadline = datetime.strptime(deadline_str, "%Y-%m-%dT%H:%M")
        except ValueError:
            flash("Invalid deadline format. Please use the date picker.")
            return redirect(url_for('job_creation'))

        new_drive = PlacementDrive(
            company_id=company.id,
            job_title=title,
            job_description=description,
            eligibility=eligibility,
            application_deadline=deadline,
            status='Pending'
        )
        db.session.add(new_drive)
        db.session.commit()
        return redirect(url_for('company_dash'))
    return render_template('company/job_creation.html')


@app.route('/company/jobs/update', methods=['POST'])
@login_required
def job_update():
    company = Company.query.filter_by(id=current_user.id).first()
    
    if company is None or company.is_approved == False or company.is_blacklisted == True:
        return redirect(url_for('company_dash'))
    
    drive_id = request.form.get('drive_id')
    status = request.form.get('status')
    drive = PlacementDrive.query.filter_by(id=drive_id, company_id=current_user.id).first()

    if drive is not None:
        drive.status = status
        db.session.commit()

    return redirect(url_for('company_dash'))


@app.route("/company/applications")
@login_required
def company_applications():
    company = Company.query.filter_by(id=current_user.id).first()

    if company is None or company.is_approved == False or company.is_blacklisted == True:
        return redirect(url_for('login'))

    drives = PlacementDrive.query.filter_by(company_id=company.id).all()

    applications = []

    for drive in drives:
        drive_apps = Application.query.filter_by(drive_id=drive.id).all()

        for app_item in drive_apps:
            applications.append(app_item)

    return render_template(
        "company/applications.html",
        applications=applications
    )
    
@app.route("/company/applications/update", methods=["POST"])
@login_required
def update_application_status():
    company = Company.query.filter_by(id=current_user.id).first()
    
    if company is None or company.is_approved == False or company.is_blacklisted == True:
        return redirect(url_for('login'))

    application_id = request.form["application_id"]
    status = request.form["status"]

    application = Application.query.filter_by(id=application_id).first()

    if application is not None:
        drive = PlacementDrive.query.filter_by(id=application.drive_id, company_id=current_user.id).first()
        
        if drive is not None:
            valid_statuses = ['Applied', 'Shortlisted', 'Interview', 'Rejected', 'Placed']
            
            if status in valid_statuses:
                application.status = status
                db.session.commit()
                send_application_status_update(application, status)

    return redirect(url_for("company_applications"))


@app.route("/company/interviews")
@login_required
def company_interviews():
    company = Company.query.filter_by(id=current_user.id).first()

    if company is None or company.is_approved == False or company.is_blacklisted == True:
        return redirect(url_for('login'))

    drives = PlacementDrive.query.filter_by(company_id=company.id).all()

    eligible_apps = []
    for drive in drives:
        apps = Application.query.filter(
            Application.drive_id == drive.id,
            Application.status.in_(['Shortlisted', 'Interview'])
        ).all()
        eligible_apps.extend(apps)

    scheduled = []
    placed = []
    for drive in drives:
        apps = Application.query.filter_by(drive_id=drive.id).all()
        for app_item in apps:
            if app_item.status == 'Placed':
                placed.append(app_item)
            elif app_item.interview:
                scheduled.append(app_item)

    return render_template(
        "company/interviews.html",
        eligible_apps=eligible_apps,
        scheduled=scheduled,
        placed=placed
    )


@app.route("/company/interviews/schedule", methods=["POST"])
@login_required
def schedule_interview():
    company = Company.query.filter_by(id=current_user.id).first()

    if company is None or company.is_approved == False or company.is_blacklisted == True:
        return redirect(url_for('login'))

    application_id = request.form.get("application_id")
    interview_date_str = request.form.get("interview_date")
    interview_link = request.form.get("interview_link", "").strip()
    venue = request.form.get("venue", "").strip()
    notes = request.form.get("notes", "").strip()

    application = Application.query.filter_by(id=application_id).first()
    if application is None:
        flash("Application not found")
        return redirect(url_for("company_interviews"))

    drive = PlacementDrive.query.filter_by(id=application.drive_id, company_id=company.id).first()
    if drive is None:
        flash("Unauthorized")
        return redirect(url_for("company_interviews"))

    try:
        interview_date = datetime.strptime(interview_date_str, "%Y-%m-%dT%H:%M")
    except (ValueError, TypeError):
        flash("Invalid date format")
        return redirect(url_for("company_interviews"))

    interview = application.interview
    if interview:
        interview.interview_date = interview_date
        interview.interview_link = interview_link
        interview.venue = venue
        interview.notes = notes
    else:
        interview = Interview(
            application_id=application.id,
            interview_date=interview_date,
            interview_link=interview_link,
            venue=venue,
            notes=notes
        )
        db.session.add(interview)

    application.status = "Interview"
    db.session.commit()
    send_interview_scheduled(interview, application)

    flash("Interview scheduled successfully")
    return redirect(url_for("company_interviews"))


@app.route("/company/interviews/delete", methods=["POST"])
@login_required
def delete_interview():
    company = Company.query.filter_by(id=current_user.id).first()

    if company is None or company.is_approved == False or company.is_blacklisted == True:
        return redirect(url_for('login'))

    interview_id = request.form.get("interview_id")
    interview = Interview.query.filter_by(id=interview_id).first()

    if interview:
        drive = PlacementDrive.query.filter_by(
            id=interview.application.drive_id, company_id=company.id
        ).first()
        if drive:
            application = interview.application
            db.session.delete(interview)
            db.session.commit()
            send_interview_cancelled(application)
            flash("Interview cancelled")

    return redirect(url_for("company_interviews"))