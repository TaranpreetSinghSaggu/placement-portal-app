from flask import Flask
from flask_login import LoginManager
from models import db, Admin, Company, Student

app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = 'it can be anything!!!!!'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///placement_portal.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db.init_app(app)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'

# User loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    """Load user by ID from any user table"""
    # Try Admin first
    user = Admin.query.get(int(user_id))
    if user:
        return user
    
    # Try Company
    user = Company.query.get(int(user_id))
    if user:
        return user
    
    # Try Student
    user = Student.query.get(int(user_id))
    if user:
        return user
    
    return None

# Create tables and default admin
with app.app_context():
    db.create_all()
    
    # Create default admin if not exists
    admin = Admin.query.filter_by(username='admin').first()
    if not admin:
        admin = Admin(username='admin')
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        print("Default admin created: admin / admin123")

# Import routes
from auth import *

if __name__ == '__main__':
    app.run(debug=True)
