from flask import render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
from app import app
from models import db, Admin, Company, Student


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
            student = Student.query.filter_by(email=email).first()
            if student and student.check_password(password):
                if not student.is_active:
                    flash('Account is deactivated')
                    return redirect(url_for('login'))
                login_user(student)
                return redirect('/student/dashboard')
            flash('Invalid email or password')

        elif user_type == 'company':
            company = Company.query.filter_by(email=email).first()
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

        if user_type == 'student':
            contact = request.form.get('contact')

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

            flash('Registration successful! Please login.')
            return redirect(url_for('login'))

        elif user_type == 'company':
            hr_contact = request.form.get('hr_contact')
            website = request.form.get('website')

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
        name = request.form.get('name')
        email = request.form.get('email')
        contact = request.form.get('contact')
        password = request.form.get('password')

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

        return redirect(url_for('login'))

    return render_template('student_register.html')


@app.route('/student/login', methods=['GET', 'POST'])
def student_login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        student = Student.query.filter_by(email=email).first()
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
        name = request.form.get('name')
        email = request.form.get('email')
        hr_contact = request.form.get('hr_contact')
        website = request.form.get('website')
        password = request.form.get('password')

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

        flash('Wait for admin approval')
        return redirect(url_for('login'))

    return render_template('company_register.html')


@app.route('/company/login', methods=['GET', 'POST'])
def company_login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        company = Company.query.filter_by(email=email).first()
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
    return render_template('home.html')


@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    return "<h1>Admin Dashboard (Coming Soon)</h1>"


@app.route('/student/dashboard')
@login_required
def student_dashboard():
    return "<h1>Student Dashboard (Coming Soon)</h1>"


@app.route('/company/dashboard')
@login_required
def company_dashboard():
    return "<h1>Company Dashboard (Coming Soon)</h1>"
