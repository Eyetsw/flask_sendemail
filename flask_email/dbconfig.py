
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

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
