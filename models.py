from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime ,timezone
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class Admin(UserMixin, db.Model):
    __tablename__ = 'admins'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<Admin {self.username}>'


class Company(UserMixin, db.Model):
    __tablename__ = 'companies'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    hr_contact = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    website = db.Column(db.String(200))
    is_approved = db.Column(db.Boolean, default=False)
    is_blacklisted = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))

    placement_drives = db.relationship(
        'PlacementDrive',
        backref='company',
        lazy=True,
        cascade='all, delete-orphan'
    )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<Company {self.name}>'


class Student(UserMixin, db.Model):
    __tablename__ = 'students'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    contact = db.Column(db.String(15), nullable=False)
    skills = db.Column(db.Text)
    resume_filename = db.Column(db.String(200))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))

    applications = db.relationship(
        'Application',
        backref='student',
        lazy=True,
        cascade='all, delete-orphan'
    )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<Student {self.name}>'


class PlacementDrive(db.Model):
    __tablename__ = 'placement_drives'

    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    job_title = db.Column(db.String(200), nullable=False)
    job_description = db.Column(db.Text, nullable=False)
    eligibility = db.Column(db.Text)
    application_deadline = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), default='Pending')
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))

    applications = db.relationship(
        'Application',
        backref='placement_drive',
        lazy=True,
        cascade='all, delete-orphan'
    )

    def __repr__(self):
        return f'<PlacementDrive {self.job_title}>'


class Application(db.Model):
    __tablename__ = 'applications'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    drive_id = db.Column(db.Integer, db.ForeignKey('placement_drives.id'), nullable=False)
    application_date = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    status = db.Column(db.String(20), default='Applied')

    placement = db.relationship(
        'Placement',
        backref='application',
        uselist=False,
        cascade='all, delete-orphan'
    )

    __table_args__ = (
        db.UniqueConstraint('student_id', 'drive_id', name='unique_student_drive'),
    )

    def __repr__(self):
        return f'<Application {self.id}>'


class Placement(db.Model):
    __tablename__ = 'placements'

    id = db.Column(db.Integer, primary_key=True)
    application_id = db.Column(
        db.Integer,
        db.ForeignKey('applications.id'),
        nullable=False,
        unique=True
    )
    placed_date = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    remarks = db.Column(db.Text)

    def __repr__(self):
        return f'<Placement {self.id}>'
