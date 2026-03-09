from flask import Flask
from flask_login import LoginManager
from flask_mail import Mail
from models import db, Admin, Company, Student

app = Flask(__name__)

app.config['SECRET_KEY'] = 'it can be anything!!!!!'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///placement_portal.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'taranpreetssaggu@gmail.com'
app.config['MAIL_PASSWORD'] = 'fnoz ekis urvp yvzw'
app.config['MAIL_DEFAULT_SENDER'] = ('Placement Portal', 'taranpreetssaggu@gmail.com')

mail = Mail(app)

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'

@login_manager.user_loader
def load_user(user_id):
    if user_id.startswith('admin_'):
        return Admin.query.get(int(user_id[6:]))
    elif user_id.startswith('company_'):
        return Company.query.get(int(user_id[8:]))
    elif user_id.startswith('student_'):
        return Student.query.get(int(user_id[8:]))
    return None

with app.app_context():
    db.create_all()
    admin = Admin.query.filter_by(username='admin').first()
    if not admin:
        admin = Admin(username='admin')
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()

from auth import *
from admin_route import *
from company_route import *
from student_route import *

if __name__ == '__main__':
    app.run("0.0.0.0", debug=True)
