import os
import secrets
from datetime import datetime
from dotenv import load_dotenv
from flask import Flask, request, render_template, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
import smtplib
from email.mime.text import MIMEText

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY') or secrets.token_hex(32)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class SendEmail(db.Model):
    __tablename__ = 'sendemail'
    id = db.Column(db.Integer, primary_key=True)
    sender_name = db.Column(db.String(120), nullable=False)
    recipient_name = db.Column(db.String(120), nullable=False)
    email_body = db.Column(db.Text, nullable=True)
    email_cc_bcc = db.Column(db.String(200), nullable=True)  
    send_time = db.Column(db.DateTime, nullable=True)
    send_success = db.Column(db.Boolean, nullable=True)


    def __init__(self, sender_name, recipient_name, email_body, email_cc_bcc, send_time, send_success):
        self.sender_name = sender_name
        self.recipient_name = recipient_name
        self.email_body = email_body
        self.email_cc_bcc = email_cc_bcc
        self.send_time = send_time
        self.send_success = send_success


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        sender_name = request.form.get('sender')
        recipient_name = request.form.get('to')
        subject = request.form.get('subject')
        email_body = request.form.get('message')
        email_cc_bcc = request.form.get('cc')

        SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))
        SMTP_SENDER = os.getenv('SMTP_SENDER')
        SMTP_PASSWORD = os.getenv('SMTP_PASSWORD')

        msg = MIMEText(email_body if email_body else "", _charset='utf-8')
        msg['Subject'] = subject if subject else "Test Subject"
        msg['From'] = sender_name
        msg['To'] = recipient_name

        if email_cc_bcc:
            msg['Cc'] = email_cc_bcc
            recipients = [recipient_name] + [cc.strip() for cc in email_cc_bcc.split(',')]
        else:
            recipients = [recipient_name]

        send_success = False
        try:
            server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
            server.starttls()
            server.login(SMTP_SENDER, SMTP_PASSWORD)
            server.sendmail(SMTP_SENDER, recipients, msg.as_string())
            server.quit()
            send_success = True
            flash("ส่งอีเมลสำเร็จ", "success")
        except Exception as e:
             flash(f"เกิดข้อผิดพลาดขณะส่งอีเมล: {str(e)}", "danger")

        try:
            new_record = SendEmail(
                sender_name=sender_name,
                recipient_name=recipient_name,
                email_body=email_body,
                email_cc_bcc=email_cc_bcc,
                send_time=datetime.now(),
                send_success=send_success
            )
            db.session.add(new_record)
            db.session.commit()
            print("บันทึกข้อมูลลง DB สำเร็จ")
        except Exception as e:
            db.session.rollback()
            flash(f"เกิดข้อผิดพลาดในการบันทึกข้อมูล: {str(e)}", "danger")
            print(f"Error committing to DB: {str(e)}")

        return redirect(url_for('index'))
    
    return render_template('send_email_form.html')

if __name__ == '__main__':
    app.run(debug=True)
