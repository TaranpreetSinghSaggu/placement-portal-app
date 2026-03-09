from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required , current_user
from app import app
from models import db, Admin, Company, Student,PlacementDrive, Application
from mail_utils import send_company_approved, send_company_blacklisted

@app.route("/admin/dashboard")
@login_required
def admin_dash():
    if not isinstance(current_user, Admin):
        return redirect(url_for('login'))
    student_count= Student.query.count()
    companies_count = Company.query.count()
    drives_count = PlacementDrive.query.count()
    applications_count = Application.query.count()

    return render_template('admin/dashboard.html', student_count=student_count,
                           companies_count=companies_count, drives_count=drives_count,
                           applications_count=applications_count)   

@app.route("/admin/companies", methods=['GET', 'POST'])
@login_required
def admin_companies():
    if not isinstance(current_user, Admin):
        return redirect(url_for('login'))
    if request.method == 'POST':
        company_id = request.form.get('company_id')
        action = request.form.get('action')

        company = Company.query.filter_by(id=company_id).first()
        if company:
            if action == 'approve':
                company.is_approved = True
                company.is_blacklisted = False
                db.session.commit()
                send_company_approved(company)
            elif action == 'blacklist':
                company.is_blacklisted = True
                company.is_approved = False
                db.session.commit()
                send_company_blacklisted(company)
            elif action == 'reject':
                company.is_approved = False
                db.session.commit()
            else:
                db.session.commit()

        return redirect(url_for('admin_companies'))
    
    search_companies = request.args.get('search_companies')

    if search_companies:
        companies = Company.query.filter(Company.name.contains(search_companies)).all()
    else:
        companies = Company.query.all()

    return render_template('admin/companies.html', companies=companies) 


@app.route("/admin/students", methods=['GET', 'POST'])
@login_required
def admin_students():
    if not isinstance(current_user, Admin):
        return redirect(url_for('login'))
    if request.method == 'POST':
        student_id = request.form.get('student_id')
        action = request.form.get('action')

        student = Student.query.filter_by(id=student_id).first()

        if student:
            if action == 'deactivate':
                student.is_active = False
            elif action == 'activate':
                student.is_active = True

            db.session.commit()
        
        return redirect(url_for('admin_students'))

    search_students = request.args.get('search_students')

    if search_students:
        students = Student.query.filter(Student.name.contains(search_students)).all()
    else:
        students = Student.query.all()

    return render_template('admin/students.html', students=students)


@app.route("/admin/drives", methods=['GET', 'POST'])
@login_required
def admin_drives():
    if not isinstance(current_user, Admin):
        return redirect(url_for('login'))
    if request.method == 'POST':
        drive_id = request.form.get('drive_id')
        action = request.form.get('action')

        drive = PlacementDrive.query.filter_by(id=drive_id).first()

        if drive:
            if action == 'approve':
                drive.status = 'Approved'
            elif action == 'reject':
                drive.status = 'Rejected'

            db.session.commit()
        return redirect(url_for('admin_drives'))
    
    drives = PlacementDrive.query.all()
    return render_template("admin/drives.html", drives=drives)


@app.route("/admin/applications")
@login_required
def admin_applications():
    if not isinstance(current_user, Admin):
        return redirect(url_for('login'))

    applications = Application.query.all()

    return render_template(
        "admin/applications.html",
        applications=applications
    )