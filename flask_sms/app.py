import requests
from flask import Flask, request, flash, render_template, redirect
import os
from dotenv import load_dotenv
from datetime import datetime
import secrets
from flask_sqlalchemy import SQLAlchemy

load_dotenv()

app = Flask(__name__)

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY') or secrets.token_hex(32)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class SendSms(db.Model):
    __tablename__ = 'sendsms'
    id = db.Column(db.Integer, primary_key=True)
    sender_name = db.Column(db.String(50), nullable=False) 
    receiver_phone = db.Column(db.String(15), nullable=False)
    message = db.Column(db.Text, nullable=False)
    sent_datetime = db.Column(db.DateTime, default=db.func.current_timestamp())
    sent_success = db.Column(db.Boolean, nullable=False)

SMS_API_URL = "https://portal-otp.smsmkt.com/api/send-message"
SENDER_NAME = os.getenv('SENDER_NAME')

@app.route('/', methods=['GET', 'POST'])
def send_sms():
    if request.method == 'POST':
        sender_name = SENDER_NAME
        recipient_phone = request.form['recipient_phone']
        message = request.form['message']

        if not recipient_phone or not message:
            flash("Recipient phone and message are required", "error")
            return redirect('/')

        
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "api_key": os.getenv("API_KEY"),
            "secret_key": os.getenv("SECRET_KEY_API")
        }
        payload = {
            'message': message,
            'phone': recipient_phone,
            'sender': sender_name,
        }

        print("Payload:", payload)
        print("Headers:", headers)

        
        response = requests.request("POST", SMS_API_URL, json=payload, headers=headers)
        print(f"API Response Status Code: {response.status_code}")
        print(response.text)

        try:
            response_data = response.json()
            print("Response JSON:", response_data)
        except ValueError:
            print("Non-JSON Response:", response.text)
            response_data = {}

        if response.status_code == 200 and response_data.get('code') == "000":
            flash("SMS sent successfully!", "success")
            sent_success = True

            try:
                new_record = SendSms(
                    sender_name=sender_name,
                    receiver_phone=recipient_phone,
                    message=message,
                    sent_datetime=datetime.now(),
                    sent_success=sent_success
                )
                db.session.add(new_record)
                db.session.commit()
                print("บันทึกข้อมูลลง DB สำเร็จ")
            except Exception as e:
                db.session.rollback()
                flash(f"เกิดข้อผิดพลาดในการบันทึกข้อมูล: {str(e)}", "danger")
                print(f"Error committing to DB: {str(e)}")
        else:
            flash(f"Failed to send SMS. Response: {response.text}", "error")
            sent_success = False

        return redirect('/')

    return render_template('send_sms_form.html')


if __name__ == '__main__':
    app.run(debug=True)
