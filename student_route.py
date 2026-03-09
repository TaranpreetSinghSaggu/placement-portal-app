import os
from flask import render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename

from app import app
from models import db, Student, PlacementDrive, Application, Company, Interview


@app.route("/student/dashboard")
@login_required
def student_dashboard():

    if not isinstance(current_user, Student):
        return redirect(url_for("login"))
    
    student = Student.query.filter_by(id=current_user.id).first()
    if student is None or student.is_active == False:
        return "<h3>Your account has been deactivated. Contact admin for more information.</h3>"

    all_drives = PlacementDrive.query.filter_by(status="Approved").all()
    
    drives = []
    for drive in all_drives:
        company = Company.query.filter_by(id=drive.company_id).first()
        if company and company.is_approved == True and company.is_blacklisted == False:
            drives.append(drive)

    recent_applications = Application.query.filter_by(
        student_id=current_user.id
    ).order_by(Application.application_date.desc()).limit(5).all()

    return render_template(
        "student/dashboard.html",
        drives=drives,
        applications=recent_applications
    )


@app.route("/student/search")
@login_required
def search_drives():

    if not isinstance(current_user, Student):
        return redirect(url_for("login"))
    
    student = Student.query.filter_by(id=current_user.id).first()
    if student is None or student.is_active == False:
        return redirect(url_for("login"))

    keyword = request.args.get("keyword")

    if keyword:
        all_drives = PlacementDrive.query.filter(
            PlacementDrive.job_title.contains(keyword)
        ).filter_by(status="Approved").all()
    else:
        all_drives = PlacementDrive.query.filter_by(status="Approved").all()
    
    drives = []
    for drive in all_drives:
        company = Company.query.filter_by(id=drive.company_id).first()
        if company and company.is_approved == True and company.is_blacklisted == False:
            drives.append(drive)

    return render_template(
        "student/search.html",
        drives=drives
    )


@app.route("/student/profile", methods=["GET", "POST"])
@login_required
def student_profile():

    if not isinstance(current_user, Student):
        return redirect(url_for("login"))

    student = Student.query.filter_by(id=current_user.id).first()
    
    if student is None or student.is_active == False:
        return redirect(url_for("login"))

    if request.method == "POST":

        student.contact = request.form["contact"]
        student.skills = request.form["skills"]

        resume = request.files.get("resume")
        if resume and resume.filename != "":
            filename = secure_filename(resume.filename)
            resume.save("static/resumes/" + filename)
            student.resume_filename = filename

        profile_pic = request.files.get("profile_pic")
        if profile_pic and profile_pic.filename != "":
            ext = os.path.splitext(profile_pic.filename)[1].lower()
            allowed = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
            if ext in allowed:
                pic_filename = f"student_{student.id}{ext}"
                profile_pic.save("static/profile_pics/" + pic_filename)
                student.profile_pic = pic_filename
            else:
                flash("Invalid image format. Use JPG, PNG, GIF or WEBP.")

        db.session.commit()

        return redirect(url_for("student_dashboard"))

    return render_template(
        "student/profile.html",
        student=student
    )


@app.route("/student/apply", methods=["POST"])
@login_required
def apply_drive():

    if not isinstance(current_user, Student):
        flash("Access denied")
        return redirect(url_for("login"))
    
    student = Student.query.filter_by(id=current_user.id).first()
    if student is None or student.is_active == False:
        flash("Your account is not active")
        return redirect(url_for("login"))

    drive_id = request.form["drive_id"]
    
    drive = PlacementDrive.query.filter_by(id=drive_id).first()
    if drive is None or drive.status != "Approved":
        flash("This placement drive is not available")
        return redirect(url_for("student_dashboard"))
    
    company = Company.query.filter_by(id=drive.company_id).first()
    if company is None or company.is_approved == False or company.is_blacklisted == True:
        flash("This company is not available for applications")
        return redirect(url_for("student_dashboard"))

    existing = Application.query.filter_by(
        student_id=current_user.id,
        drive_id=drive_id
    ).first()

    if existing is None:

        application = Application(
            student_id=current_user.id,
            drive_id=drive_id,
            status="Applied"
        )

        db.session.add(application)
        db.session.commit()
        
        flash("Application submitted successfully")
    else:
        flash("You have already applied to this drive")

    return redirect(url_for("student_dashboard"))


@app.route("/student/applications")
@login_required
def student_applications():

    if not isinstance(current_user, Student):
        return redirect(url_for("login"))
    
    student = Student.query.filter_by(id=current_user.id).first()
    if student is None or student.is_active == False:
        return redirect(url_for("login"))

    applications = Application.query.filter_by(
        student_id=current_user.id
    ).order_by(Application.application_date.desc()).all()

    return render_template(
        "student/applications.html",
        applications=applications
    )


@app.route("/student/interviews")
@login_required
def student_interviews():

    if not isinstance(current_user, Student):
        return redirect(url_for("login"))

    student = Student.query.filter_by(id=current_user.id).first()
    if student is None or student.is_active == False:
        return redirect(url_for("login"))

    applications = Application.query.filter_by(
        student_id=current_user.id
    ).all()

    interviews = []
    placed = []
    for app_item in applications:
        if app_item.status == 'Placed':
            placed.append(app_item)
        elif app_item.interview:
            interviews.append(app_item)

    return render_template(
        "student/interviews.html",
        interviews=interviews,
        placed=placed
    )
