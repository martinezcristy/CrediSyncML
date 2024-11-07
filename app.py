from flask import Flask, render_template, request, jsonify
#redirect, url_for, flash
# from flask_mail import Mail
from flask_mysqldb import MySQL 
from flask_mail import Mail
from flask_mysqldb import MySQL
# from models import Member
from dotenv import load_dotenv
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import json

load_dotenv()

# Create Flask app instance
app = Flask(__name__)

# SQL values from env
MYSQL_HOST = os.getenv('SQL_HOSTNAME')
MYSQL_USER = os.getenv('SQL_USERNAME')
MYSQL_PASSWORD = os.getenv('SQL_PASSWORD')
MYSQL_DB = os.getenv('SQL_DB')

# Email values from env
EMAIL_SERVER = os.getenv("MAIL_SERVER")
EMAIL_PORT = int(os.getenv("MAIL_PORT"))  
EMAIL_USE_TLS = bool(int(os.getenv("MAIL_USE_TLS")))
EMAIL_USERNAME = os.getenv("MAIL_USERNAME")
EMAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
EMAIL_DEFAULT_SENDER = os.getenv("MAIL_DEFAULT_SENDER")

app.secret_key = os.getenv('SECRET_KEY', 'your_default_secret_key')  # Ensure you have a secret key for session management

#MYSQL CONFIGURATION
app.config['MYSQL_HOST'] = MYSQL_HOST
app.config['MYSQL_USER'] = MYSQL_USER
app.config['MYSQL_PASSWORD'] = MYSQL_PASSWORD
app.config['MYSQL_DB'] = MYSQL_DB
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

#EMAIL CONFIGURATION
app.config.update(
    MAIL_SERVER=EMAIL_SERVER,
    MAIL_PORT=EMAIL_PORT,
    MAIL_USE_TLS=EMAIL_USE_TLS,
    MAIL_USERNAME=EMAIL_USERNAME,
    MAIL_PASSWORD=EMAIL_PASSWORD,
    MAIL_DEFAULT_SENDER=EMAIL_DEFAULT_SENDER,
)

mail = Mail(app)

# Initialize MySQL
mysql = MySQL(app)

# Load subscription plans from JSON file
def load_subscriptions():
    with open('subscriptions.json') as f:
        return json.load(f)

# Dashboard route
@app.route('/', methods=['GET'])
def dashboard():
    subscriptions = load_subscriptions()
    return render_template('dashboard.html', subscriptions=subscriptions)

# Members route
@app.route('/members', methods=['GET', 'POST'])
def members():
     # Save the member to the database
    cur = mysql.connection.cursor()

    if request.method == 'POST':
        # Retrieve form data
        account_number = request.form['account-number']
        name = request.form['name']
        contact_number = request.form['contact-number']
        email = request.form['email-address']
        address = request.form['address']
        date_applied = request.form['date-applied']

        try:
            cur.execute("INSERT INTO members (account_number, name, contact_number, email, address, date_applied) VALUES (%s, %s, %s, %s, %s, %s)", (account_number, name, contact_number, email, address, date_applied))
            mysql.connection.commit()
            # Return success response
            return jsonify({"success": True}), 200
        except Exception as e:
            mysql.connection.rollback()  # In case of an error, rollback
            return jsonify({"success": False, "error": str(e)}), 500

    cur.execute("SELECT * FROM members")
    members_data = cur.fetchall() #fetch from sql db inag start ani nga route
    cur.close()

    # return render_template('members.html')
    return render_template('members.html', members=members_data)

@app.route('/send_approval_email', methods=['POST'])
def send_approval_email_route():
    recipient = request.json.get('recipient')  # Extract the recipient gikan sa members html
    applicant_name = request.json.get('applicantName')  # Get the applicant's name
    if recipient:
        subject = "Credisync - Loan Application Approved"
        # message = "Your request has been approved!"

         # Get the path sa html email content mao ni ma display sa email 
        html_file_path = os.path.join('templates', 'email.html')

        # Read the HTML content
        try:
            with open(html_file_path, 'r') as file:
                html_content = file.read()
                # Replace placeholders with actual values
                html_content = html_content.replace("[SUBJECT HERE]", subject)
                html_content = html_content.replace("[BODY HERE]", f"Dear {applicant_name}, we are pleased to inform you that your credisync loan application has been approved.")
                html_content = html_content.replace("[APPNAME HERE]", "CREDISYNC")
        except Exception as e:
            return jsonify({"error": f"Failed to read email template: {str(e)}"}), 500

        # Create the email
        msg = MIMEMultipart()
        msg['From'] = EMAIL_USERNAME
        msg['To'] = recipient
        msg['Subject'] = subject

        # Attach the HTML content to the email
        msg.attach(MIMEText(html_content, 'html'))
        
        # text = f"Subject: {subject}\n\n{message}"

        try:
            with smtplib.SMTP(EMAIL_SERVER, EMAIL_PORT) as server:
                server.starttls()
                server.login(EMAIL_USERNAME, EMAIL_PASSWORD)
                server.sendmail(EMAIL_USERNAME, recipient, msg.as_string())
            return jsonify({"message": "Email sent successfully!"}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    return jsonify({"error": "Recipient not provided."}), 400

# Settings route
@app.route('/settings', methods=['GET', 'POST'])
def settings():
    return render_template('settings.html')

# Evaluation route
@app.route('/evaluation')
def evaluation():
    return render_template('evaluation.html')

# Approve route
@app.route('/approveMember')
def approve():
    return 'test approve'

@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404


if __name__ == "__main__":
    app.run(debug=True)