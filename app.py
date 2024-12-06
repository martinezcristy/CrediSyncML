from flask import Flask, render_template, request, jsonify, session, g, redirect, url_for, render_template_string
from flask_session import Session
from flask_bcrypt import Bcrypt
import bcrypt
from flask_mysqldb import MySQL 
from flask_mail import Mail
from dotenv import load_dotenv
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import smtplib
import json
import joblib
import numpy  as np


load_dotenv()

# Create Flask app instance
app = Flask(__name__)
# Initialize Bcrypt
bcrypt = Bcrypt(app)

app.secret_key = os.getenv('SECRET_KEY')
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

# SQL values from env
MYSQL_HOST = os.getenv('SQL_HOSTNAME')
MYSQL_USER = os.getenv('SQL_USERNAME')
MYSQL_PASSWORD = os.getenv('SQL_PASSWORD')
MYSQL_DB = os.getenv('SQL_DB')

# Initialize MySQL
mysql = MySQL(app)

# Email values from env
EMAIL_SERVER = os.getenv("MAIL_SERVER")
EMAIL_PORT = int(os.getenv("MAIL_PORT"))  
EMAIL_USE_TLS = bool(int(os.getenv("MAIL_USE_TLS")))
EMAIL_USERNAME = os.getenv("MAIL_USERNAME")
EMAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
EMAIL_DEFAULT_SENDER = os.getenv("MAIL_DEFAULT_SENDER")

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

#Load the model
ELIGIBILITY_MODEL = joblib.load('decision_tree_model.pkl')

# Check if user is logged in, allowed access to signup
@app.before_request 
def before_request(): 
    g.user = None 
    if 'cooperative_id' in session: 
        g.user = session['cooperative_id']
    elif request.endpoint not in ('login', 'signup', 'static'):
        return redirect(url_for('login'))

# Load subscription plans data from JSON file
def load_subscriptions():
    with open('subscriptions.json') as f:
        return json.load(f)
    
# Login route 
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        cooperative_id = request.form['cooperative_id']
        password = request.form['password']

        # Assuming you are using flask-mysqldb for DB connection, adjust if necessary
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM user WHERE cooperative_id = %s', (cooperative_id,))
        user = cursor.fetchone()
        cursor.close()

        if user:
            # Compare entered password with stored hashed password
            if bcrypt.check_password_hash(user['password'], password):  # Correct method for checking hashed password
                session.pop('error', None)  # Clear any previous error messages
                session['logged_in'] = True
                session['cooperative_id'] = user['cooperative_id']  # Store cooperative_id in session
                session['cooperative_name'] = user['cooperative_name']  # Store cooperative_name in session
                return redirect(url_for('dashboard'))
            else:
                session['error'] = 'Invalid credentials. Please try again.'
                return redirect(url_for('login'))
        else:
            session['error'] = 'Invalid credentials. Please try again.'
            return redirect(url_for('login'))

    # Success or error messages from session
    success_message = session.pop('success', None)  # Get success message if available
    error_message = session.pop('error', None)  # if entered wrong credentials
    return render_template('login.html', success=success_message, error=error_message)



# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     if request.method == 'POST':
#         cooperative_id = request.form['cooperative_id']
#         password = request.form['password']

#         cursor = mysql.connection.cursor()
#         cursor.execute('SELECT * FROM user WHERE cooperative_id = %s', (cooperative_id,))
#         user = cursor.fetchone()
#         cursor.close()

#         if user:
#             stored_password = user['password'].encode('utf-8')
#             entered_password = password.encode('utf-8')

#             # Debugging logs
#             print(f"Stored Password: {stored_password}")
#             print(f"Entered Password: {entered_password}")

#             if bcrypt.checkpw(entered_password, stored_password):
#                 session.pop('error', None)  # Clear any previous error messages
#                 session['user_id'] = user['cooperative_id']
#                 return redirect(url_for('dashboard'))
#             else:
#                 session['error'] = 'Invalid credentials. Please try again.'
#                 return redirect(url_for('login'))
#         else:
#             session['error'] = 'Invalid credentials. Please try again.'
#             return redirect(url_for('login'))
#     success_message = session.pop('success', None) # Get success message if available
#     error_message = session.pop('error', None) #if entered wrong credentials
#     return render_template('login.html', success=success_message, error=error_message)

# Logout route
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))

# Signup route
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        cooperative_id = request.form['cooperative_id']
        cooperative_name = request.form['cooperative_name']
        address = request.form['address']
        contact_number = request.form['contact_number']
        password = request.form['password']

        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM user WHERE cooperative_id = %s', (cooperative_id,))
        existing_user = cursor.fetchone()
        if existing_user:
            session['error'] = 'Cooperative ID already exists. Please try a different ID.'
            cursor.close()
            return redirect(url_for('signup'))

        # hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        try:
            # cursor.execute('INSERT INTO user (cooperative_id, password, cooperative_name, address, contact_number) VALUES (%s, %s, %s, %s, %s)',
            #                (cooperative_id, hashed_password.decode('utf-8'), cooperative_name, address, contact_number))
            cursor.execute('INSERT INTO user (cooperative_id, password, cooperative_name, address, contact_number) VALUES (%s, %s, %s, %s, %s)',
                        (cooperative_id, hashed_password, cooperative_name, address, contact_number))
            mysql.connection.commit()
            session.pop('error', None)  # Clear any previous error messages
            session['success'] = 'User account successfully created!'
            cursor.close()
            return redirect(url_for('login'))
        except Exception as e:
            session['error'] = str(e)
            cursor.close()
            return redirect(url_for('signup'))
    
    error_message = session.pop('error', None)
    return render_template('signup.html', error_message=error_message)

# Dashboard route
@app.route('/', methods=['GET'])
def dashboard():
    if not g.user:
        return redirect(url_for('login'))
    cooperative_name = session.get('cooperative_name')
    subscriptions = load_subscriptions()
    return render_template('dashboard.html', subscriptions=subscriptions, cooperative_name=cooperative_name)

# @app.route('/', methods=['GET'])
# def dashboard():
#     cur = mysql.connection.cursor()

#     try:
#         # Total number of members
#         cur.execute("SELECT COUNT(*) FROM members")
#         all_members_count = cur.fetchone()[0]

#         # Total number of declined members
#         cur.execute("SELECT COUNT(*) FROM declined_members")
#         declined_members_count = cur.fetchone()[0]

#         # Close cursor
#         cur.close()

#         # Load subscription json
#         subscriptions = load_subscriptions()  # Replace with your subscription loading logic

#         return render_template('dashboard.html',
#                                all_members_count=all_members_count,
#                                declined_members_count=declined_members_count,
#                                subscriptions=subscriptions)

#     except mysql.connect.Error as e:
#         # Handle database errors
#         return jsonify({"error": f"Database error: {str(e)}"}), 500

#     except Exception as e:
#         # Handle other unexpected errors (optional)
#         return jsonify({"error": "An unexpected error occurred."}), 500

@app.route('/members', methods=['GET', 'POST'])
def members():
    
    coop_id = session.get('cooperative_id')  # Get cooperative_id from session
    cooperative_name = session.get('cooperative_name') # Get cooperative_name from session
    print(f"Cooperative ID from session: {coop_id}")  # Debugging log

    if request.method == 'POST':
        # Retrieve form data
        account_number = request.form['account-number']
        name = request.form['name']
        contact_number = request.form['contact-number']
        email = request.form['email-address']
        address = request.form['address']
        date_applied = request.form['date-applied']

        # Validate if account number or email already exists in the database for this cooperative
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM members WHERE cooperative_id = %s AND (account_number = %s OR email = %s)", (coop_id, account_number, email))
        existing_member = cur.fetchone()

        if existing_member:
            # If a duplicate is found, return an error message in JSON format
            error_message = "A member with the same credentials already exists!"
            if existing_member[2] == account_number:
                error_message = "A member with this account number already exists."
            elif existing_member[4] == email:
                error_message = "Email address already exists."

            cur.close()
            return jsonify({"success": False, "error": error_message})

        try:
            cur.execute("INSERT INTO members (cooperative_id, account_number, name, contact_number, email, address, date_applied, status) VALUES (%s, %s, %s, %s, %s, %s, %s, 'Pending')", (coop_id, account_number, name, contact_number, email, address, date_applied))
            mysql.connection.commit()
            # session.pop('error', None)  # Clear any previous error messages
            # session['success'] = 'Member successfully added!'
            cur.close()
            # return redirect(url_for('members'))
            return jsonify({"success": True})
        except Exception as e:
            mysql.connection.rollback()  # In case of an error, rollback
            # session['error'] = str(e)
            cur.close()
            # return redirect(url_for('members'))
            return jsonify({"success": False, "error": str(e)})

   # Fetch members for this cooperative
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM members WHERE cooperative_id = %s", (coop_id,))
    members_data = cur.fetchall()
    cur.close()

    # Get success or error messages from session
    error_message = session.pop('error', None)
    success_message = session.pop('success', None)

    return render_template('members.html', members=members_data, error_message=error_message, success_message=success_message, cooperative_name=cooperative_name)


# Declined  members route
@app.route('/decline_member', methods=['POST'])
def decline_member():
    # Decline using account number
    account_number = request.json.get('account_number')

    if not account_number:
        return jsonify({"error": "Account number not provided"}), 400

    coop_id = session.get('cooperative_id')  # Get cooperative_id from session
    cur = mysql.connection.cursor()

    try:
        # Retrieve the member details from members table using account number and cooperative_id
        cur.execute("SELECT * FROM members WHERE account_number = %s AND cooperative_id = %s", (account_number, coop_id))
        member = cur.fetchone()

        if not member:
            return jsonify({"error": "Member not found"}), 404

        # Update the member's status to 'Declined' in members table
        cur.execute("UPDATE members SET status = 'Declined' WHERE account_number = %s AND cooperative_id = %s", (account_number, coop_id))

        # Insert the declined member into declined_members table
        cur.execute("INSERT INTO declined_members (account_number, name, contact_number, email, address, date_applied, status, cooperative_id) VALUES (%s, %s, %s, %s, %s, %s, 'Declined', %s)",
                    (member['account_number'], member['name'], member['contact_number'], member['email'], member['address'], member['date_applied'], coop_id))

        # Delete the member from the members table, but keep it for now for dashboard display
        # cur.execute("DELETE FROM members WHERE account_number = %s AND cooperative_id = %s", (account_number, coop_id))
        mysql.connection.commit()
        
        return jsonify({"message": "Member declined successfully!"}), 200
    except Exception as e:
        mysql.connection.rollback()  # Rollback in case of error
        return jsonify({"error": str(e)}), 500
    finally:
        cur.close()


# Route for sending the approval notification thru email
@app.route('/send_approval_email', methods=['POST'])
def send_approval_email_route():
    data = request.json
    recipient = data.get('recipient')
    applicant_name = data.get('applicantName')
    account_number = data.get('accountNumber')
    
    # Fetch evaluation details from evaluated_members table
    try:
        conn = mysql.connection
        cur = conn.cursor()
        cur.execute("SELECT * FROM evaluated_members WHERE account_number = %s", (account_number,))
        evaluation_details = cur.fetchone()
        cur.close()
    except Exception as e:
        return jsonify({"error": f"Failed to fetch evaluation details: {str(e)}"}), 500

    if not evaluation_details:
        return jsonify({"error": "No evaluation details found for the member."}), 404

    if recipient:
        subject = "Credisync - Loan Application Approved"
        app_name = "CREDISYNC"
        
        # Get the path to the email template
        html_file_path = os.path.join('templates', 'approved-email.html')

        # Get the current date and time 
        current_date = datetime.now().strftime('%Y-%m-%d')

        # Read the HTML content
        try:
            with open(html_file_path, 'r') as file:
                html_content = file.read()

                # Replace placeholders with actual values from database
                html_content = html_content.replace("[SUBJECT HERE]", subject)
                html_content = html_content.replace("[DATE_APPROVED]", current_date)
                html_content = html_content.replace("[APPLICANT NAME]", str(evaluation_details.get('name', 'N/A')))
                html_content = html_content.replace("[ACCOUNT NUMBER]", str(evaluation_details.get('account_number', 'N/A')))
                html_content = html_content.replace("[APPLICATION DATE]", str(evaluation_details.get('date_applied', 'N/A')))
                # html_content = html_content.replace("[LOAN AMOUNT]", str(evaluation_details.get('loan_amount', 'N/A')))
                html_content = html_content.replace("[EVALUATION DATE]", str(evaluation_details.get('date_evaluated', 'N/A')))
                html_content = html_content.replace("[CURRENTLY EMPLOYED]", str(evaluation_details.get('payment_history', 'N/A')))
                html_content = html_content.replace("[LOAN TERM]", str(evaluation_details.get('loan_term', 'N/A')))
                html_content = html_content.replace("[CO-MAKER]", str(evaluation_details.get('co_maker', 'N/A')))
                html_content = html_content.replace("[MONTHLY SALARY]", str(evaluation_details.get('monthly_salary', 'N/A')))
                html_content = html_content.replace("[ASSET OWNER]", str(evaluation_details.get('asset_owner', 'N/A')))
                html_content = html_content.replace("[REPAYMENT SCHEDULE]", str(evaluation_details.get('repayment_schedule', 'N/A')))
                html_content = html_content.replace("[PAYMENT METHOD]", str(evaluation_details.get('payment_method', 'N/A')))
                html_content = html_content.replace("[CREDIT SCORE]", str(evaluation_details.get('credit_score', 'N/A')))
                html_content = html_content.replace("[ELIGIBILITY RESULT]", str(evaluation_details.get('prediction', 'N/A')))
                html_content = html_content.replace("[APPNAME HERE]", app_name)

        except Exception as e:
            return jsonify({"error": f"Failed to read email template: {str(e)}"}), 500

        # Create the email
        msg = MIMEMultipart()
        msg['From'] = EMAIL_USERNAME
        msg['To'] = recipient
        msg['Subject'] = subject

        # Attach the HTML content to the email
        msg.attach(MIMEText(html_content, 'html'))

        try:
            with smtplib.SMTP(EMAIL_SERVER, EMAIL_PORT) as server:
                server.starttls()
                server.login(EMAIL_USERNAME, EMAIL_PASSWORD)
                server.sendmail(EMAIL_USERNAME, recipient, msg.as_string())
            return jsonify({"message": "Email sent successfully!"}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    return jsonify({"error": "Recipient not provided."}), 400


# Route for sending the decline notification thru email
@app.route('/send_declined_email', methods=['POST'])
def send_declined_email_route():
    data = request.json
    recipient = request.json.get('recipient')  # Extract the recipient gikan sa members html
    applicant_name = request.json.get('applicantName')  # Get the applicant's name
    if recipient:
        subject = "Credisync - Loan Application Declined"

         # Get the path sa html email content mao ni ma display sa email 
        html_file_path = os.path.join('templates', 'declined-email.html')

        # Read the HTML content
        try:
            with open(html_file_path, 'r') as file:
                html_content = file.read()
                # Replace placeholders with actual values
                html_content = html_content.replace("[SUBJECT HERE]", subject)
                html_content = html_content.replace("[BODY HERE]", f"Dear {applicant_name}, we are sad to inform you that your credisync loan application has been declined.")
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


# Route to update member information
@app.route('/update_member_status', methods=['POST'])
def update_member_status():
    data = request.json
    account_number = data.get('account_number')  # Account number is read-only
    status = data.get('status')
    email = data.get('email')  # Include this in checking

    if not account_number or not status:
        return jsonify({"error": "Account number or status not provided"}), 400

    coop_id = session.get('cooperative_id')  # Get cooperative_id from session
    cur = mysql.connection.cursor()

    try:
        # Check if email exists (excluding the current member and within the same cooperative)
        cur.execute("SELECT * FROM members WHERE email = %s AND account_number != %s AND cooperative_id = %s", (email, account_number, coop_id))
        email_exists = cur.fetchone()

        if email_exists:
            return jsonify({"error": "Email already exists for another account within the same cooperative"}), 409

        # Update the member's status (within the same cooperative)
        cur.execute("UPDATE members SET status = %s WHERE account_number = %s AND cooperative_id = %s", (status, account_number, coop_id))
        mysql.connection.commit()

        return jsonify({"success": True}), 200
    except Exception as e:
        mysql.connection.rollback()  # Rollback in case of error
        return jsonify({"error": str(e)}), 500
    finally:
        cur.close()


# Profile route
@app.route('/settings', methods=['GET', 'POST'])
def settings():
    cooperative_name = session.get('cooperative_name')
    coop_id = session.get('cooperative_id')
    if not coop_id:
        return redirect(url_for('login'))

    if request.method == 'POST':
        try:
            data = request.get_json()
            coop_name = data['coop_name']
            address = data['address']
            contact_number = data['contact_number']

            cur = mysql.connection.cursor()
            cur.execute("""
                UPDATE user
                SET cooperative_name = %s, address = %s, contact_number = %s
                WHERE cooperative_id = %s
            """, (coop_name, address, contact_number, coop_id))
            mysql.connection.commit()
            cur.close()

            return jsonify({"message": "User updated successfully!"}), 200
        except Exception as e:
            mysql.connection.rollback()
            return jsonify({"error": str(e)}), 500
    else:
        cur = mysql.connection.cursor()
        cur.execute("SELECT cooperative_id, cooperative_name, address, contact_number FROM user WHERE cooperative_id = %s", (coop_id,))
        user = cur.fetchone()
        cur.close()
        if user:
            return render_template('settings.html', user=user, cooperative_name=cooperative_name)
        return jsonify({"error": "User not found"}), 404
    
# @app.route('/settings', methods=['POST'])
# def settings():
#     try:
#         data = request.get_json()
#         cooperative_id = data['cooperative_id']
#         coop_name = data['coop_name']
#         address = data['address']
#         contact_number = data['contact_number']
#         email = data['email']

#         cur = mysql.connection.cursor()
#         cur.execute("""
#             UPDATE user
#             SET cooperative_name = %s, address = %s, contact_number = %s, email = %s
#             WHERE cooperative_id = %s
#         """, (coop_name, address, contact_number, email, cooperative_id))
#         mysql.connection.commit()
#         cur.close()

#         return jsonify({"message": "User updated successfully!"}), 200
#     except Exception as e:
#         mysql.connection.rollback()
#         return jsonify({"error": str(e)}), 500


# # Route to fetch user details
# @app.route('/get_user', methods=['GET'])
# def get_user():
#     cur = mysql.connection.cursor()
#     try:
#         cur.execute("SELECT cooperative_id, cooperative_name, address, contact_number, email FROM user LIMIT 1")
#         user = cur.fetchone()

#         if not user:
#             return jsonify({"error": "User not found"}), 404

#         user_data = {
#             "cooperative_id": user['cooperative_id'], 
#             "cooperative_name": user['cooperative_name'], 
#             "address": user['address'], 
#             "contact_number": user['contact_number'], 
#             "email": user['email']
#         }
#         return jsonify(user_data), 200
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500
#     finally:
#         cur.close()

@app.route('/evaluation', methods=['GET', 'POST'])
def evaluation():
    cooperative_name = session.get('cooperative_name')
    cooperative_id = session.get('cooperative_id')
    try:
        if request.method == 'GET':
            account_number = request.args.get('account_number')

            if not account_number:
                return jsonify({"error": "Account number not provided"}), 400

            cur = mysql.connection.cursor()

            try:
                cur.execute("SELECT * FROM members WHERE account_number = %s", (account_number,))
                member = cur.fetchone()

                if not member:
                    return jsonify({"error": "Member not found"}), 404

                return render_template('evaluation.html', member=member, cooperative_name=cooperative_name)

            except Exception as e:
                app.logger.error(f"Database error: {str(e)}")
                return jsonify({"error": "Error fetching member data"}), 500
            finally:
                cur.close()

        elif request.method == 'POST':
        
            form_data = request.form
            account_number = form_data.get('account_number')

            app.logger.info(f"Received Account Number: {account_number}")

            # If account_number is missing or invalid, return an error
            if not account_number:
                return jsonify({"error": "Account number is missing or invalid."}), 400
            
            # map values to store plain text
            currently_employed_map = {
                "50": "After the due date",
                "80": "Within the due date",
                "100": "Before the due date"
            }
            monthly_salary_map = {
                "50": "P11,300 below",
                "80": "P11,301 to P41,299",
                "100": "P41,300 above"
            }
            loan_term_map = {
                "50": "85 months above (Mortgage)",
                "80": "60 to 84 months (Auto Loans)",
                "100": "12 to 60 months (Personal)"
            }
            co_maker_map = {
                "50": "No co-maker",
                "80": "Co-maker with moderate reliability",
                "100": "Co-maker with strong reliability"
            }
            savings_account_map = {
                "50": "No Savings Account",
                "80": "Not Active",
                "100": "Active"
            }
            asset_owner_map = {
                "50": "No assets",
                "80": "Owns properties/vehicle",
                "100": "Owns both properties and vehicle"
            }
            payment_method_map = {
                "50": "Cash",
                "80": "Post-dated Check",
                "100": "Debit to Savings Account"
            }
            repayment_schedule_map = {
                "50": "Quarterly",
                "80": "Monthly",
                "100": "Weekly"
            }

            currently_employed = currently_employed_map.get(form_data.get('currently_employed'), '')
            monthly_salary = monthly_salary_map.get(form_data.get('Monthly_Salary'), '')
            loan_term = loan_term_map.get(form_data.get('Loan_Term'), '')
            co_maker = co_maker_map.get(form_data.get('Co_Maker'), '')
            savings_account = savings_account_map.get(form_data.get('Savings_Account'), '')
            asset_owner = asset_owner_map.get(form_data.get('Asset_Owner'), '')
            payment_method = payment_method_map.get(form_data.get('Payment_Method'), '')
            repayment_schedule = repayment_schedule_map.get(form_data.get('Repayment_Schedule'), '')

            # Get the credit score
            credit_score = int(form_data.get('Credit_Score', 0))

            # Log the form data to inspect the values
            app.logger.info("Received form data:")
            for key, value in form_data.items():
                app.logger.info(f"{key}: {value}")

            required_fields = [
                'Monthly_Salary', 'Loan_Term',
                'Co_Maker', 'Savings_Account', 'Asset_Owner',
                'Payment_Method', 'Repayment_Schedule', 'Credit_Score'
            ]

            missing_fields = [field for field in required_fields if not form_data.get(field)]
            if missing_fields:
                return jsonify({"error": f"Missing required fields: {', '.join(missing_fields)}"}), 400

            features = [
                float(form_data.get('Monthly_Salary')),
                float(form_data.get('Loan_Term')),
                float(form_data.get('Co_Maker')),
                float(form_data.get('Savings_Account')),
                float(form_data.get('Asset_Owner')),
                float(form_data.get('Payment_Method')),
                float(form_data.get('Repayment_Schedule')),
                float(form_data.get('Credit_Score', 0))
            ]

            features_array = np.array([features])

            # Assuming you have a pre-loaded model
            eligibility_prediction = ELIGIBILITY_MODEL.predict(features_array)[0]
            eligibility_text = 'Eligible for a loan' if eligibility_prediction == 1 else 'Not eligible for a loan'

            app.logger.info(f"Prediction result - Eligibility: {eligibility_text}")

             # Get the current date as the evaluation date
            evaluation_date = datetime.now().strftime('%Y-%m-%d')

             # Save evaluation details to the evaluated_members table
            name = form_data.get('name')
            contact_number = form_data.get('contact_number')
            email = form_data.get('email')
            address = form_data.get('address')

            #  # evaluation details
            # currently_employed = form_data.get('currently_employed') #this is Payment History field in the eval form
            # monthly_salary = form_data.get('Monthly_Salary')
            # loan_term = form_data.get('Loan_Term')
            # co_maker = form_data.get('Co_Maker')
            # savings_account = form_data.get('Savings_Account')
            # asset_owner = form_data.get('Asset_Owner')
            # payment_method = form_data.get('Payment_Method')
            # repayment_schedule = form_data.get('Repayment_Schedule')

            cur = mysql.connection.cursor()

            try:
                # save to evaluated_members table
                cur.execute("""
                    INSERT INTO evaluated_members (
                        account_number, name, contact_number, email, address, date_applied, status, credit_score, 
                        prediction, date_evaluated, payment_history, monthly_salary, loan_term, co_maker, 
                        savings_account, asset_owner, payment_method, repayment_schedule, cooperative_id
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    account_number, form_data.get('name'), form_data.get('contact_number'), form_data.get('email'),
                    form_data.get('address'), form_data.get('dateapplied'), 'Evaluated', 
                    credit_score, eligibility_text, datetime.now().strftime('%Y-%m-%d'), 
                    currently_employed, monthly_salary, loan_term, 
                    co_maker, savings_account, asset_owner, 
                    payment_method, repayment_schedule, cooperative_id
                ))

                # Commit the changes
                mysql.connection.commit()

                # Now, update the member's status in the original members table
                cur.execute("UPDATE members SET status = 'Evaluated' WHERE account_number = %s", (account_number,))
                mysql.connection.commit()

            except Exception as e:
                app.logger.error(f"Error saving evaluation data: {str(e)}")
                return jsonify({"error": "Error saving evaluation data"}), 500
            finally:
                cur.close()

            # # Return the result as JSON
            return jsonify({'eligibility': eligibility_text})

    except Exception as e:
        app.logger.error(f"Unexpected error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500
    

# Member profile page 
@app.route('/member-profile/<account_number>')
def member_profile(account_number):
    cooperative_name = session.get('cooperative_name')
    cur = mysql.connection.cursor()
    try:
        # Fetch member details based on account number
        cur.execute("SELECT * FROM members WHERE account_number = %s", (account_number,))
        member = cur.fetchone()

        # Close cursor
        cur.close()

        success_message = session.pop('success', None) # Get success message if available

        if member:
            return render_template('member-profile.html', member=member, success=success_message, cooperative_name=cooperative_name)
        else:
            return "Member not found", 404

    except Exception as e:
        cur.close()
        return jsonify({"error": str(e)}), 500

# Edit member route  
@app.route('/update-member', methods=['POST'])
def update_member():
    try:
        account_number = request.form['account_number']
        name = request.form['name']
        contact_number = request.form['contact_number']
        email = request.form['email']
        address = request.form['address']

        coop_id = session.get('cooperative_id')  # Get cooperative_id from session
        cur = mysql.connection.cursor()

        # Update member details in the database for the specific cooperative
        cur.execute("""
            UPDATE members
            SET name = %s, contact_number = %s, email = %s, address = %s
            WHERE account_number = %s AND cooperative_id = %s
        """, (name, contact_number, email, address, account_number, coop_id))
        
        mysql.connection.commit()
        cur.close()
        
        # Set success message in session
        session['success'] = 'Member information updated successfully.'

        return redirect(url_for('member_profile', account_number=account_number))
    except KeyError as e:
        return jsonify({"error": f"Missing form field: {str(e)}"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
# 500 error handler
@app.errorhandler(500)
def page_not_found(error):
    return render_template('404.html'), 500

# 405 error handler
@app.errorhandler(405)
def page_not_found(error):
    return render_template('404.html'), 405

# 404 error handler
@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404

# 400 error handler
@app.errorhandler(400)
def bad_request(error):
    return render_template('404.html'), 400


if __name__ == "__main__":
    app.run(debug=True)

# if __name__ == "__main__":
# app.run(debug=True, host='0.0.0.0')
