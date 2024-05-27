import os

import requests
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_mail import Mail, Message

load_dotenv()

email_user = os.environ.get('EMAIL_USER')
email_password = os.environ.get('EMAIL_PASSWORD')
recaptcha_api_key = os.environ.get('RECAPTCHA_API_KEY')

target_api_url = 'https://www.google.com/recaptcha/api/siteverify'
allowed_origins = ['http://localhost:3000', 'https://tabhang.github.io', 'https://tejasa.dev']

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": allowed_origins}})

# Configure Flask-Mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = email_user
app.config['MAIL_PASSWORD'] = email_password
app.config['MAIL_DEFAULT_SENDER'] = email_user

mail = Mail(app)  # Initialize Flask-Mail


@app.route('/api/verify', methods=['POST'])
def verify():
    try:
        recaptcha_response = request.json['token']
        recaptcha_data = {
            'secret': recaptcha_api_key,
            'response': recaptcha_response
        }

        response = requests.post(target_api_url, data=recaptcha_data)
        response_data = response.json()

        print('Response from target API:', response_data)

        if response_data['success']:
            form_data = request.json['formData']

            mail_subject = f"[Contact-Form] Message from {form_data['name']}"
            mail_body = form_data['message']
            to_email = email_user
            reply_to = form_data['email']

            # Use Flask-Mail to send email
            message = Message(mail_subject, recipients=[to_email], reply_to=reply_to)
            message.body = mail_body
            mail.send(message)

            return jsonify({'status': True})

        else:
            return jsonify({'status': False})

    except Exception as e:
        print('Error:', str(e))
        return jsonify({'error': 'Internal Server Error'}), 500


@app.route('/')
def index():
    return 'Flask on google cloud run'


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
