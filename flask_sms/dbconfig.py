from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class SendSms(db.Model):
    __tablename__ = 'sendsms'
    id = db.Column(db.Integer, primary_key=True)
    sender_name = db.Column(db.String(50), nullable=False) 
    receiver_phone = db.Column(db.String(15), nullable=False)
    message = db.Column(db.Text, nullable=False)
    sent_datetime = db.Column(db.DateTime, server_default=db.func.current_timestamp())
    sent_success = db.Column(db.Boolean, nullable=False)
