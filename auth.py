from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_user, logout_user, login_required
from app import app
from models import db, Admin, Company, Student, PlacementDrive, Application
from mail_utils import send_student_welcome, send_company_welcome


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_type = request.form.get('user_type')
        email = request.form.get('email')
        password = request.form.get('password')

        if user_type == 'admin':
            admin = Admin.query.filter_by(username=email).first()
            if admin and admin.check_password(password):
                login_user(admin)
                return redirect('/admin/dashboard')
            flash('Invalid admin credentials')

        elif user_type == 'student':
            student = Student.query.filter_by(email=email.strip().lower()).first()
            if student and student.check_password(password):
                if not student.is_active:
                    flash('Account is deactivated')
                    return redirect(url_for('login'))
                login_user(student)
                return redirect('/student/dashboard')
            flash('Invalid email or password')

        elif user_type == 'company':
            company = Company.query.filter_by(email=email.strip().lower()).first()
            if company and company.check_password(password):
                if not company.is_approved:
                    flash('Account not approved yet')
                    return redirect(url_for('login'))
                if company.is_blacklisted:
                    flash('Account is blacklisted')
                    return redirect(url_for('login'))
                login_user(company)
                return redirect('/company/dashboard')
            flash('Invalid email or password')

        else:
            flash('Please select a user type')

    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        user_type = request.form.get('user_type')
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')

        if len(password) < 6:
            flash('Password must be at least 6 characters')
            return redirect(url_for('register'))

        if user_type == 'student':
            contact = request.form.get('contact', '').strip()
            name = name.strip()
            email = email.strip().lower()

            if not name or not email or not contact:
                flash('All fields are required')
                return redirect(url_for('register'))

            if Student.query.filter_by(email=email).first():
                flash('Email already registered')
                return redirect(url_for('register'))

            student = Student(
                name=name,
                email=email,
                contact=contact,
                is_active=True
            )
            student.set_password(password)
            db.session.add(student)
            db.session.commit()
            send_student_welcome(student)

            flash('Registration successful! Please login.')
            return redirect(url_for('login'))

        elif user_type == 'company':
            name = request.form.get('comp_name', '').strip()
            email = request.form.get('comp_email', '').strip().lower()
            hr_contact = request.form.get('hr_contact', '').strip()
            website = request.form.get('website', '').strip() or None

            if not name or not email or not hr_contact:
                flash('All fields are required')
                return redirect(url_for('register'))

            if Company.query.filter_by(email=email).first():
                flash('Email already registered')
                return redirect(url_for('register'))

            company = Company(
                name=name,
                email=email,
                hr_contact=hr_contact,
                website=website,
                is_approved=False,
                is_blacklisted=False
            )
            company.set_password(password)
            db.session.add(company)
            db.session.commit()
            send_company_welcome(company)

            flash('Registration successful! Wait for admin approval before logging in.')
            return redirect(url_for('login'))

        else:
            flash('Please select a user type')

    return render_template('register.html')


@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        admin = Admin.query.filter_by(username=username).first()
        if admin and admin.check_password(password):
            login_user(admin)
            return redirect('/admin/dashboard')

        flash('Invalid admin credentials')

    return render_template('admin_login.html')


@app.route('/student/register', methods=['GET', 'POST'])
def student_register():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        contact = request.form.get('contact', '').strip()
        password = request.form.get('password', '')

        if not name or not email or not contact:
            flash('All fields are required')
            return redirect(url_for('student_register'))

        if len(password) < 6:
            flash('Password must be at least 6 characters')
            return redirect(url_for('student_register'))

        if Student.query.filter_by(email=email).first():
            flash('Email already registered')
            return redirect(url_for('student_register'))

        student = Student(
            name=name,
            email=email,
            contact=contact,
            is_active=True
        )
        student.set_password(password)
        db.session.add(student)
        db.session.commit()
        send_student_welcome(student)

        flash('Registration successful! Please login.')
        return redirect(url_for('student_login'))

    return render_template('student_register.html')


@app.route('/student/login', methods=['GET', 'POST'])
def student_login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        student = Student.query.filter_by(email=email.strip().lower()).first()
        if student and student.check_password(password):
            if not student.is_active:
                flash('Account is deactivated')
                return redirect(url_for('login'))

            login_user(student)
            return redirect('/student/dashboard')

        flash('Invalid email or password')

    return render_template('student_login.html')


@app.route('/company/register', methods=['GET', 'POST'])
def company_register():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        hr_contact = request.form.get('hr_contact', '').strip()
        website = request.form.get('website', '').strip() or None
        password = request.form.get('password', '')

        if not name or not email or not hr_contact:
            flash('All fields are required')
            return redirect(url_for('company_register'))

        if len(password) < 6:
            flash('Password must be at least 6 characters')
            return redirect(url_for('company_register'))

        if Company.query.filter_by(email=email).first():
            flash('Email already registered')
            return redirect(url_for('company_register'))

        company = Company(
            name=name,
            email=email,
            hr_contact=hr_contact,
            website=website,
            is_approved=False,
            is_blacklisted=False
        )
        company.set_password(password)

        db.session.add(company)
        db.session.commit()
        send_company_welcome(company)

        flash('Registration successful! Wait for admin approval before logging in.')
        return redirect(url_for('company_login'))

    return render_template('company_register.html')


@app.route('/company/login', methods=['GET', 'POST'])
def company_login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        company = Company.query.filter_by(email=email.strip().lower()).first()
        if company and company.check_password(password):
            if not company.is_approved:
                flash('Account not approved yet')
                return redirect(url_for('login'))

            if company.is_blacklisted:
                flash('Account is blacklisted')
                return redirect(url_for('login'))

            login_user(company)
            return redirect('/company/dashboard')

        flash('Invalid email or password')

    return render_template('company_login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/')
def index():
    stats = {
        'students': Student.query.count(),
        'companies': Company.query.filter_by(is_approved=True).count(),
        'drives': PlacementDrive.query.filter_by(status='Approved').count(),
        'applications': Application.query.count(),
        'placed': Application.query.filter_by(status='Placed').count(),
    }
    return render_template('home.html', stats=stats)


@app.route('/api/analytics')
def api_analytics():
    statuses = ['Applied', 'Shortlisted', 'Interview', 'Placed', 'Rejected']
    status_counts = {s: Application.query.filter_by(status=s).count() for s in statuses}

    drive_statuses = ['Pending', 'Approved', 'Rejected']
    drive_counts = {s: PlacementDrive.query.filter_by(status=s).count() for s in drive_statuses}

    companies = Company.query.filter_by(is_approved=True).all()
    company_drives = []
    for c in companies:
        count = PlacementDrive.query.filter_by(company_id=c.id, status='Approved').count()
        if count > 0:
            company_drives.append({'name': c.name, 'drives': count})
    company_drives.sort(key=lambda x: x['drives'], reverse=True)
    top_companies = company_drives[:6]

    return jsonify({
        'application_statuses': status_counts,
        'drive_statuses': drive_counts,
        'top_companies': top_companies,
    })

