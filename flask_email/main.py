import os
import secrets
from datetime import datetime
from dotenv import load_dotenv
from flask import Flask, request, render_template, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
import smtplib
from email.mime.text import MIMEText
from dbconfig import db, SendEmail

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY') or secrets.token_hex(32)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

@app.route('/api/create_send_email', methods=['POST'])
def create_send_email():
    data = request.json
    print("Received data",data)
    if request.method == 'GET':
        return jsonify({"message": "This endpoint expects POST requests with JSON body."}), 200

    if not request.is_json:
        return jsonify({"error": "Content-Type must be application/json"}), 415

    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400

    sender_name = data.get('sender')
    recipient_name = data.get('to')
    subject = data.get('subject')
    email_body = data.get('message')
    email_cc_bcc = data.get('cc')
    additional_text = data.get('additional_text', '')

    if not sender_name or not recipient_name:
        return jsonify({"error": "Missing required fields: 'sender' and/or 'to'"}), 400

    full_message = (email_body if email_body else "")
    if additional_text:
        full_message += "\n\n" + additional_text

    SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
    SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))
    SMTP_SENDER = os.getenv('SMTP_SENDER')
    SMTP_PASSWORD = os.getenv('SMTP_PASSWORD')

    msg = MIMEText(full_message, _charset='utf-8')
    msg['Subject'] = subject if subject else "Test Subject"
    msg['From'] = sender_name
    msg['To'] = recipient_name

    if email_cc_bcc:
        msg['Cc'] = email_cc_bcc
        recipients = [recipient_name] + [cc.strip() for cc in email_cc_bcc.split(',')]
    else:
        recipients = [recipient_name]

    send_success = False
    error_msg = ""
    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_SENDER, SMTP_PASSWORD)
        server.sendmail(SMTP_SENDER, recipients, msg.as_string())
        server.quit()
        send_success = True
    except Exception as e:
        error_msg = str(e)

    try:
        new_record = SendEmail(
            sender_name=sender_name,
            recipient_name=recipient_name,
            email_body=full_message,
            email_cc_bcc=email_cc_bcc,
            send_time=datetime.now(),
            send_success=send_success
        )
        db.session.add(new_record)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Error data: {str(e)}")
        return jsonify({"error": f"Error saving to database: {str(e)}"}), 500

    if send_success:
        return jsonify({
            "message": "Email sent successfully",
            "record_id": new_record.id,
            "additional_text": additional_text
        }), 200
    else:
        return jsonify({"error": f"Failed to send email: {error_msg}"}), 500

@app.route('/api/status', methods=['GET'])
def status():
    return jsonify({"status": "API is running"}), 200

if __name__ == '__main__':
    app.run(debug=True)
