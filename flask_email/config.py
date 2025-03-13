import os
from dotenv import load_dotenv

load_dotenv()

#SMTP
SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))
SMTP_SENDER = os.getenv('SMTP_SENDER', 'juthaporn.tsw@gmail.com')
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD')

SECRET_KEY = os.getenv('SECRET_KEY')
DATABASE_URL = os.getenv('DATABASE_URL')
