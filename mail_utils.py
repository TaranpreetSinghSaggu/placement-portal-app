from flask_mail import Message
from app import mail


def _send(subject, recipient, html):
    try:
        msg = Message(subject=subject, recipients=[recipient], html=html)
        mail.send(msg)
    except Exception:
        pass


def send_student_welcome(student):
    html = f"""
    <div style="font-family:Segoe UI,sans-serif;max-width:600px;margin:auto;border:1px solid #e5e7eb;border-radius:10px;overflow:hidden">
      <div style="background:#4338CA;padding:28px 32px">
        <h2 style="color:#fff;margin:0">Welcome to Placement Portal</h2>
      </div>
      <div style="padding:32px">
        <p style="font-size:16px;color:#1f2937">Hi <strong>{student.name}</strong>,</p>
        <p style="color:#374151">Your student account has been successfully created. You can now log in and start browsing placement drives.</p>
        <table style="margin:24px 0;border-collapse:collapse;width:100%">
          <tr><td style="padding:8px 12px;background:#f3f4f6;border-radius:6px;color:#6b7280;width:130px">Registered Email</td>
              <td style="padding:8px 12px;color:#1f2937"><strong>{student.email}</strong></td></tr>
          <tr><td style="padding:8px 12px;color:#6b7280">Contact</td>
              <td style="padding:8px 12px;color:#1f2937">{student.contact}</td></tr>
        </table>
        <p style="color:#374151">Complete your profile by uploading your resume and adding your skills to improve your chances of getting shortlisted.</p>
        <p style="margin-top:32px;color:#6b7280;font-size:13px">— Placement Portal Team</p>
      </div>
    </div>
    """
    _send("Welcome to Placement Portal 🎓", student.email, html)


def send_company_welcome(company):
    html = f"""
    <div style="font-family:Segoe UI,sans-serif;max-width:600px;margin:auto;border:1px solid #e5e7eb;border-radius:10px;overflow:hidden">
      <div style="background:#4338CA;padding:28px 32px">
        <h2 style="color:#fff;margin:0">Company Registration Received</h2>
      </div>
      <div style="padding:32px">
        <p style="font-size:16px;color:#1f2937">Hi <strong>{company.name}</strong>,</p>
        <p style="color:#374151">Thank you for registering on the Placement Portal. Your account is currently <strong>pending admin approval</strong>. You will receive another email once your account is approved.</p>
        <table style="margin:24px 0;border-collapse:collapse;width:100%">
          <tr><td style="padding:8px 12px;background:#f3f4f6;border-radius:6px;color:#6b7280;width:130px">Company</td>
              <td style="padding:8px 12px;color:#1f2937"><strong>{company.name}</strong></td></tr>
          <tr><td style="padding:8px 12px;color:#6b7280">Email</td>
              <td style="padding:8px 12px;color:#1f2937">{company.email}</td></tr>
          <tr><td style="padding:8px 12px;color:#6b7280">HR Contact</td>
              <td style="padding:8px 12px;color:#1f2937">{company.hr_contact}</td></tr>
        </table>
        <p style="margin-top:32px;color:#6b7280;font-size:13px">— Placement Portal Team</p>
      </div>
    </div>
    """
    _send("Company Registration — Pending Approval", company.email, html)


def send_company_approved(company):
    html = f"""
    <div style="font-family:Segoe UI,sans-serif;max-width:600px;margin:auto;border:1px solid #e5e7eb;border-radius:10px;overflow:hidden">
      <div style="background:#10B981;padding:28px 32px">
        <h2 style="color:#fff;margin:0">Account Approved ✅</h2>
      </div>
      <div style="padding:32px">
        <p style="font-size:16px;color:#1f2937">Hi <strong>{company.name}</strong>,</p>
        <p style="color:#374151">Your company account has been <strong>approved</strong> by the admin. You can now log in to the portal and start posting placement drives.</p>
        <p style="margin-top:32px;color:#6b7280;font-size:13px">— Placement Portal Team</p>
      </div>
    </div>
    """
    _send("Your Company Account is Approved 🎉", company.email, html)


def send_company_blacklisted(company):
    html = f"""
    <div style="font-family:Segoe UI,sans-serif;max-width:600px;margin:auto;border:1px solid #e5e7eb;border-radius:10px;overflow:hidden">
      <div style="background:#EF4444;padding:28px 32px">
        <h2 style="color:#fff;margin:0">Account Blacklisted</h2>
      </div>
      <div style="padding:32px">
        <p style="font-size:16px;color:#1f2937">Hi <strong>{company.name}</strong>,</p>
        <p style="color:#374151">Your company account has been <strong>blacklisted</strong> by the admin. You will no longer be able to access the portal. If you believe this is an error, please contact the placement cell directly.</p>
        <p style="margin-top:32px;color:#6b7280;font-size:13px">— Placement Portal Team</p>
      </div>
    </div>
    """
    _send("Company Account Blacklisted", company.email, html)


def send_application_status_update(application, new_status):
    student = application.student
    drive = application.drive

    status_colours = {
        'Shortlisted': '#F59E0B',
        'Interview':   '#6366F1',
        'Placed':      '#10B981',
        'Rejected':    '#EF4444',
    }
    status_messages = {
        'Shortlisted': 'Congratulations! You have been <strong>shortlisted</strong> for the next round.',
        'Interview':   'An interview has been scheduled for you. Please check the Interviews section on the portal for details.',
        'Placed':      '🎉 Congratulations! You have been <strong>placed</strong> at this company. Best wishes for your career!',
        'Rejected':    'We regret to inform you that your application was not selected this time. Keep applying!',
    }

    colour = status_colours.get(new_status, '#4338CA')
    message = status_messages.get(new_status, f'Your application status has been updated to <strong>{new_status}</strong>.')

    html = f"""
    <div style="font-family:Segoe UI,sans-serif;max-width:600px;margin:auto;border:1px solid #e5e7eb;border-radius:10px;overflow:hidden">
      <div style="background:{colour};padding:28px 32px">
        <h2 style="color:#fff;margin:0">Application Update — {new_status}</h2>
      </div>
      <div style="padding:32px">
        <p style="font-size:16px;color:#1f2937">Hi <strong>{student.name}</strong>,</p>
        <p style="color:#374151">{message}</p>
        <table style="margin:24px 0;border-collapse:collapse;width:100%">
          <tr><td style="padding:8px 12px;background:#f3f4f6;border-radius:6px;color:#6b7280;width:130px">Company</td>
              <td style="padding:8px 12px;color:#1f2937"><strong>{drive.company.name}</strong></td></tr>
          <tr><td style="padding:8px 12px;color:#6b7280">Job Title</td>
              <td style="padding:8px 12px;color:#1f2937">{drive.job_title}</td></tr>
          <tr><td style="padding:8px 12px;color:#6b7280">Status</td>
              <td style="padding:8px 12px"><span style="background:{colour};color:#fff;padding:4px 12px;border-radius:12px;font-size:13px">{new_status}</span></td></tr>
        </table>
        <p style="margin-top:32px;color:#6b7280;font-size:13px">— Placement Portal Team</p>
      </div>
    </div>
    """
    _send(f"Application Update: {new_status} — {drive.job_title}", student.email, html)


def send_interview_scheduled(interview, application):
    student = application.student
    drive = application.drive

    date_str = interview.interview_date.strftime("%d %B %Y, %I:%M %p")

    link_row = f"""<tr><td style="padding:8px 12px;color:#6b7280">Interview Link</td>
                   <td style="padding:8px 12px"><a href="{interview.interview_link}" style="color:#4338CA">{interview.interview_link}</a></td></tr>""" if interview.interview_link else ""

    venue_row = f"""<tr><td style="padding:8px 12px;color:#6b7280">Venue</td>
                    <td style="padding:8px 12px;color:#1f2937">{interview.venue}</td></tr>""" if interview.venue else ""

    notes_row = f"""<tr><td style="padding:8px 12px;color:#6b7280">Notes</td>
                    <td style="padding:8px 12px;color:#1f2937">{interview.notes}</td></tr>""" if interview.notes else ""

    html = f"""
    <div style="font-family:Segoe UI,sans-serif;max-width:600px;margin:auto;border:1px solid #e5e7eb;border-radius:10px;overflow:hidden">
      <div style="background:#6366F1;padding:28px 32px">
        <h2 style="color:#fff;margin:0">Interview Scheduled 📅</h2>
      </div>
      <div style="padding:32px">
        <p style="font-size:16px;color:#1f2937">Hi <strong>{student.name}</strong>,</p>
        <p style="color:#374151">Your interview has been scheduled. Here are the details:</p>
        <table style="margin:24px 0;border-collapse:collapse;width:100%">
          <tr><td style="padding:8px 12px;background:#f3f4f6;border-radius:6px;color:#6b7280;width:130px">Company</td>
              <td style="padding:8px 12px;color:#1f2937"><strong>{drive.company.name}</strong></td></tr>
          <tr><td style="padding:8px 12px;color:#6b7280">Job Title</td>
              <td style="padding:8px 12px;color:#1f2937">{drive.job_title}</td></tr>
          <tr><td style="padding:8px 12px;color:#6b7280">Date &amp; Time</td>
              <td style="padding:8px 12px;color:#1f2937"><strong>{date_str}</strong></td></tr>
          {link_row}
          {venue_row}
          {notes_row}
        </table>
        <p style="color:#374151">Please be on time and prepare accordingly. Log in to the portal to view full details in the <strong>My Interviews</strong> section.</p>
        <p style="margin-top:32px;color:#6b7280;font-size:13px">— Placement Portal Team</p>
      </div>
    </div>
    """
    _send(f"Interview Scheduled — {drive.company.name} ({drive.job_title})", student.email, html)


def send_interview_cancelled(application):
    student = application.student
    drive = application.drive

    html = f"""
    <div style="font-family:Segoe UI,sans-serif;max-width:600px;margin:auto;border:1px solid #e5e7eb;border-radius:10px;overflow:hidden">
      <div style="background:#EF4444;padding:28px 32px">
        <h2 style="color:#fff;margin:0">Interview Cancelled</h2>
      </div>
      <div style="padding:32px">
        <p style="font-size:16px;color:#1f2937">Hi <strong>{student.name}</strong>,</p>
        <p style="color:#374151">Your scheduled interview for the following position has been <strong>cancelled</strong> by the company:</p>
        <table style="margin:24px 0;border-collapse:collapse;width:100%">
          <tr><td style="padding:8px 12px;background:#f3f4f6;border-radius:6px;color:#6b7280;width:130px">Company</td>
              <td style="padding:8px 12px;color:#1f2937"><strong>{drive.company.name}</strong></td></tr>
          <tr><td style="padding:8px 12px;color:#6b7280">Job Title</td>
              <td style="padding:8px 12px;color:#1f2937">{drive.job_title}</td></tr>
        </table>
        <p style="color:#374151">Please check the portal for further updates on your application.</p>
        <p style="margin-top:32px;color:#6b7280;font-size:13px">— Placement Portal Team</p>
      </div>
    </div>
    """
    _send(f"Interview Cancelled — {drive.company.name}", student.email, html)
