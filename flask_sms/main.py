import requests
from flask import Flask, request, jsonify
import os
from dotenv import load_dotenv
from datetime import datetime
import secrets
from dbconfig import db, SendSms

load_dotenv()

app = Flask(__name__)

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY') or secrets.token_hex(32)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

SMS_API_URL = "https://portal-otp.smsmkt.com/api/send-message"

@app.route('/api/create_send_sms', methods=['POST'])
def create_send_sms():
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 415

    data = request.get_json()
    print("Received data:", data)

    sender_name = data.get('sender_name')
    recipient_phone = data.get('recipient_phone')
    message = data.get('message')

    if not sender_name or not recipient_phone or not message:
        return jsonify({"error": "sender_name, recipient_phone, and message are required"}), 400

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

    try:
        response = requests.post(SMS_API_URL, json=payload, headers=headers)
    except Exception as e:
        return jsonify({"error": f"Error sending SMS request: {str(e)}"}), 500

    print(f"API Response Status Code: {response.status_code}")
    print(response.text)

    try:
        response_data = response.json()
        print("Response JSON:", response_data)
    except ValueError:
        print("Non-JSON Response:", response.text)
        response_data = {}

    if response.status_code == 200 and response_data.get('code') == "000":
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
            print("Saved record to DB successfully")
        except Exception as e:
            db.session.rollback()
            print(f"Error data: {str(e)}")
            return jsonify({"error": f"Error saving to database: {str(e)}"}), 500

        return jsonify({
            "message": "SMS sent successfully!",
            "record_id": new_record.id,
            "response": response_data
        }), 200
    else:
        return jsonify({
            "error": f"Failed to send SMS. Response: {response.text}",
            "response": response_data
        }), 500

if __name__ == '__main__':
    app.run(debug=True)
