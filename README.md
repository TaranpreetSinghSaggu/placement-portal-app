# Placement Portal

A Flask web app connecting students, companies, and an admin for campus placements.

- **Admin** — approves companies and drives, manages students
- **Company** — posts placement drives, reviews applications, schedules interviews
- **Student** — browses drives, applies, tracks application and interview status

## Stack

Python · Flask · SQLAlchemy (SQLite) · Flask-Login · Flask-Mail · Bootstrap 5

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Run

```bash
python app.py
```

App runs at `http://localhost:5000`

## Seed Demo Data

```bash
python seed.py
```

## Default Credentials

| Role | Username / Email | Password |
|---|---|---|
| Admin | `admin` | `admin123` |
| Company | `hr@techcorp.in` | `company123` |
| Student | `aarav@college.edu` | `student123` |



All sending is wrapped in `try/except` — a failed email never crashes the app.

---

## Key Python / Flask Concepts Used

| Concept | Where Used |
|---|---|
| `@app.route()` | Every route in auth/admin/company/student files |
| `@login_required` | All protected routes |
| `current_user` | Identify the logged-in user in any route |
| `db.Model` | All 7 database tables are Python classes |
| `db.relationship` + `backref` | Navigate between related records (e.g., `application.student`) |
| `db.session.add()` + `db.session.commit()` | Create/update database records |
| `render_template()` | Render Jinja2 HTML templates |
| `request.form` / `request.files` / `request.args` | Read POST form data / uploaded files / GET params |
| `flash()` + `get_flashed_messages()` | One-time user feedback messages |
| `redirect()` + `url_for()` | Navigate between routes after POST (PRG pattern) |
| `datetime.strptime()` / `strftime()` | Parse and format date strings from HTML inputs |
| `jsonify()` | Return JSON from the `/api/analytics` endpoint |
| `isinstance(current_user, Model)` | Role-based access control |
| `secure_filename()` | Sanitise uploaded file names |

