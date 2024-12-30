from flask import Flask, render_template, request, jsonify, session, g, redirect, url_for, flash
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
import random
import uuid

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
# @app.before_request 
# def before_request(): 
#     g.user = None 
#     if 'cooperative_id' in session: 
#         g.user = session['cooperative_id']
#     elif request.endpoint not in ('login', 'signup', 'static'):
#         return redirect(url_for('login'))

@app.before_request
def before_request():
    g.user = None
    g.member = None
    
    # Check if a cooperative is logged in
    if 'cooperative_id' in session:
        g.user = {
            'id': session['cooperative_id'],
            'name': session.get('cooperative_name')
        }
    # Check if a member is logged in
    elif 'account_number' in session:
        g.member = {
            'account_number': session['account_number'],
            'firstname': session.get('firstname'),
            'lastname': session.get('lastname'),
            'email': session.get('email')
        }
    # Redirect if neither cooperative nor member is logged in and the route isn't public
    elif request.endpoint not in ('login', 'memberlogin', 'signup', 'static'):
        return redirect(url_for('login'))



# Load subscription plans data from JSON file
def load_subscriptions():
    with open('subscriptions.json') as f:
        return json.load(f)
    
# Cooperative Login route 
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session.clear()

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


@app.route('/memberlogin', methods=['GET', 'POST'])
def memberlogin():
    if request.method == 'POST':
        session.clear()

        account_number = request.form['account_number']
        password = request.form['password']

        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM members WHERE account_number = %s", (account_number,))
        user = cursor.fetchone()
        cursor.close()

        if user:
            if bcrypt.check_password_hash(user['password'], password):
                session.pop('error', None)
                session['logged_in'] = True
                session['account_number'] = user['account_number']
                session['firstname'] = user['firstname']
                session['lastname'] = user['lastname']
                session['email'] = user['email']

                return redirect(url_for('member_dashboard'))
            else:
                session['error'] = "Incorrect password. Please try again."
                return redirect(url_for('memberlogin'))
        else:
            session['error'] = "Invalid account number. Please check your details and try again."
            return redirect(url_for('memberlogin'))

    success_message = session.pop('success', None)
    error_message = session.pop('error', None)
    return render_template('member-login.html', success=success_message, error=error_message)


@app.route('/member-dashboard')
def member_dashboard():
    if g.member:
        member_account_number = f"{g.member['account_number']}"
        member_name = f"{g.member['firstname']} {g.member['lastname']}"
        member_email = f"{g.member['email']}"
        return render_template('member-dashboard.html', member_name=member_name, member_email=member_email, member_account_number=member_account_number)
    else:
        return redirect(url_for('memberlogin'))
    

# @app.route('/loanapplication-form')
# def loan_application_form():
#     if g.member:  # Ensure the user is logged in
#         # Pass member details to the form
#         return render_template(
#             'loanapplication-form.html',
#             member={
#                 'account_number': g.member['account_number'],
#                 'firstname': g.member['firstname'],
#                 'lastname': g.member['lastname'],
#                 'email': g.member['email'],
#                 'cooperative_id': g.member['cooperative_id']
#             }
#         )
#     else:
#         return redirect(url_for('memberlogin'))

@app.route('/loanapplication-form')
def loan_application_form():
    if 'logged_in' in session:  
        account_number = session.get('account_number')
        cooperative_id = session.get('cooperative_id')  
        
        # If no cooperative_id in the session, query it from the database
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT cooperative_id FROM members WHERE account_number = %s", (account_number,))
        cooperative_id = cursor.fetchone()['cooperative_id']
        cursor.close()

        # Pass account number, cooperative_id, firstname, lastname, and email to the loan application form
        return render_template(
            'loanapplication-form.html',
            account_number=account_number,
            cooperative_id=cooperative_id,
            firstname=session.get('firstname'),
            lastname=session.get('lastname'),
            email=session.get('email')
        )
    else:
        return redirect(url_for('memberlogin'))

# Helper function to insert data
def insert_into_db(cursor, query, params):
    cursor.execute(query, params)

# Route to handle the loan application form submission
@app.route('/submit_loan_application', methods=['POST'])
def submit_loan_application():
    try:
        loan_application_number = str(uuid.uuid4())  # Generate unique ID
        account_number = request.form.get('account_number')  # Hidden input from form
        cooperative_id = request.form.get('cooperative_id')
        loan_type = request.form.get('Loan_Type')
        loan_term = request.form.get('Loan_Term')
        payment_method = request.form.get('Payment_Method')
        repayment_schedule = request.form.get('Repayment_Schedule')
        loan_amount = request.form.get('Loan_Amount')

        # Step 1 - Loan Information
        loan_application_data = (
            loan_application_number, account_number, cooperative_id, 
            loan_type, loan_term, payment_method, repayment_schedule, loan_amount
        )

        # Step 2 - Personal Information
        personal_info_data = (
            request.form['lastname'], request.form['firstname'], request.form['middlename'],
            request.form['present_address'], request.form['provincial_address'], request.form['contact_number'],
            request.form['civil_status'], request.form['gender'], request.form['email']
        )

        # Step 3 - Employment Information
        employment_info_data = (
            request.form['employer_name'], request.form['position'], request.form['employer_address'], 
            request.form['employment_status'], request.form['employer_contact_number'], datetime.now().strftime('%Y-%m-%d')
        )

        cursor = mysql.connection.cursor()

        # Insert loan application with loan_status defaulting to 'Pending'
        insert_into_db(cursor, """
            INSERT INTO loan_applications (
                loan_application_number, account_number, cooperative_id, 
                loan_type, loan_term, payment_method, repayment_schedule, loan_amount, 
                lastname, firstname, middlename, present_address, provincial_address, 
                contact_number, civil_status, gender, email, 
                employer_name, position, employer_address, employment_status, 
                employer_contact_number, application_date, loan_status
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 
                      %s, %s, %s, %s, %s, %s, 'Pending')
        """, loan_application_data + personal_info_data + employment_info_data)

        # Step 4 - Co-Makers Information
        if request.form.get('co_maker_toggle') == 'on':
            co_maker_id = str(uuid.uuid4())  # Generate unique ID for co-maker
            co_maker_data = (
                co_maker_id, loan_application_number, account_number,
                request.form.get('co_maker_lastname'), request.form.get('co_maker_firstname'), 
                request.form.get('co_maker_middlename'), request.form.get('co_maker_present_address'), 
                request.form.get('co_maker_provincial_address'), request.form.get('co_maker_contact'), 
                request.form.get('co_maker_civil_status'), request.form.get('co_maker_gender'), 
                request.form.get('co_maker_email'), request.form.get('co_maker_employer_name'), 
                request.form.get('co_maker_position'), request.form.get('co_maker_employer_address'), 
                request.form.get('co_maker_employment_status'), request.form.get('co_maker_employer_contact_number'), 
                request.form.get('co_maker_net_take_home_salary')
            )
            insert_into_db(cursor, """
                INSERT INTO co_makers_info (
                    co_maker_id, loan_application_number, account_number, co_maker_lastname, 
                    co_maker_firstname, co_maker_middlename, co_maker_present_address, 
                    co_maker_provincial_address, co_maker_contact, co_maker_civil_status, 
                    co_maker_gender, co_maker_email, co_maker_employer_name, 
                    co_maker_position, co_maker_employer_address, co_maker_employment_status, 
                    co_maker_employer_contact_number, co_maker_net_take_home_salary
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, co_maker_data)

        # Step 5 - Assets Information
        if request.form.get('assets_toggle') == 'on':
            asset_types = request.form.getlist('asset_type[]')
            registration_number = request.form.get('registration_number')
            estimated_value = request.form.get('estimated_value')
            ownership_status = request.form.get('ownership_status')
            year_acquired = request.form.get('year_acquired')

            if asset_types:  # Proceed only if asset_types is not empty
                for asset_type in asset_types:
                    asset_id = str(uuid.uuid4())  # Generate unique ID for each asset
                    asset_data = (
                        asset_id, loan_application_number, account_number, asset_type, 
                        registration_number, estimated_value, ownership_status, year_acquired
                    )
                    insert_into_db(cursor, """
                        INSERT INTO assets_info (
                            asset_id, loan_application_number, account_number, asset_type, 
                            registration_number, estimated_value, ownership_status, year_acquired
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """, asset_data)

        # Commit changes to the database
        mysql.connection.commit()
        flash('Loan application submitted successfully!', 'success')
        return redirect(url_for('member_dashboard'))

    except Exception as e:
        mysql.connection.rollback()  # Roll back in case of error
        flash(f'Error submitting loan application: {e}', 'danger')
        return redirect(url_for('loan_application_form'))


# @app.route('/loanapplication-form')
# def loan_application_form():
#     if g.member:  # Ensure user is logged in
#         account_number = request.args.get("account_number")
        
#         if not account_number:
#             return redirect(url_for('memberlogin'))  # Redirect if no account number exists
#         return render_template('loanapplication-form.html', account_number=account_number)  # Pass account number
#     else:
#         return redirect(url_for('memberlogin'))

# @app.route('/member-dashboard')
# def member_dashboard():
#     if not g.user or g.user['type'] != 'member':
#         return redirect(url_for('memberlogin'))

#     # Access member data from g.user
#     account_number = g.user.get('account_number')
#     firstname = g.user.get('firstname')
#     lastname = g.user.get('lastname')
#     email = g.user.get('email')

#     if session.get('logged_in'):
#         return render_template('member-dashboard.html',
#                                 account_number=account_number, 
#                                 firstname=firstname, 
#                                 lastname=lastname, 
#                                 email=email)
#     else:
#         return redirect(url_for('memberlogin'))

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

# Cooperative Logout route
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))

@app.route('/memberlogout')
def memberlogout():
    session.pop('account_number', None)
    return redirect(url_for('memberlogin'))

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

# Generate random 8-digit account number
def generate_account_number():
    return random.randint(10000000, 99999999)


# Send login credentials via email
def send_credentials_email(recipient_email, account_number, firstname, lastname):
    subject = "Credisync - Member Credentials"
    html_content = f"""
    <html>
      <body>
        <p>Dear {firstname} {lastname},</p>
        <p>Your account number and login credentials for CREDISYNC are as follows:</p>
        <ul>
          <li>Account Number: {account_number}</li>
        </ul>
        <p>Thank you for applying!</p>
      </body>
    </html>
    """

    msg = MIMEMultipart()
    msg['From'] = EMAIL_USERNAME
    msg['To'] = recipient_email
    msg['Subject'] = subject
    msg.attach(MIMEText(html_content, 'html'))

    try:
        with smtplib.SMTP(EMAIL_SERVER, EMAIL_PORT) as server:
            server.starttls()
            server.login(EMAIL_USERNAME, EMAIL_PASSWORD)
            server.sendmail(EMAIL_USERNAME, recipient_email, msg.as_string())
            return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False


@app.route('/applicantsignup', methods=['GET', 'POST'])
def applicantsignup():
    if request.method == 'POST':
        # Extract form data (only required fields)
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        email = request.form['email']
        password = request.form['password']  # New password field

        # Hash the password
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        # Generate account number using your account number generator function
        account_number = generate_account_number()

        # Database connection
        cursor = mysql.connection.cursor()

        try:
            # Insert user signup data into the database
            cursor.execute(
                '''INSERT INTO members (account_number, firstname, lastname, email, password, status) 
                VALUES (%s, %s, %s, %s, %s, %s)''',
                (
                    account_number, firstname, lastname, email, hashed_password, 'Pending'  # Added hashed_password
                )
            )
            mysql.connection.commit()

            # Send login credentials email
            if send_credentials_email(email, account_number, firstname, lastname):
                session['success'] = 'Your account has been created successfully. Please check your email for your credentials.'
            else:
                session['error'] = 'Account created, but failed to send email.'

        except Exception as e:
            session['error'] = str(e)
        finally:
            cursor.close()

        return redirect(url_for('memberlogin'))
    
    # Handle error messages for rendering in the frontend
    error_message = session.pop('error', None)
    return render_template('applicant-signup.html', error=error_message)


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
    cooperative_name = session.get('cooperative_name')  # Get cooperative_name from session

    # Fetch loan applications for this cooperative
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT 
            account_number, lastname, firstname, email, loan_status
        FROM loan_applications 
        WHERE cooperative_id = %s
    """, (coop_id,))
    loan_applications_list = cur.fetchall()
    cur.close()

    return render_template(
        'members.html', 
        loan_applications_list=loan_applications_list,
        cooperative_name=cooperative_name
    )



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

        # # Send the decline email
        # send_decline_email(member)
        
        return jsonify({"message": "Member declined successfully!"}), 200
    except Exception as e:
        mysql.connection.rollback()  # Rollback in case of error
        return jsonify({"error": str(e)}), 500
    finally:
        cur.close()


@app.route('/send_decline_email', methods=['POST'])
def send_decline_email_route():
    data = request.json
    recipient = data.get('recipient')
    applicant_name = data.get('applicantName')
    account_number = data.get('accountNumber')
    
    # Fetch member details from members table
    try:
        conn = mysql.connection
        cur = conn.cursor()
        cur.execute("SELECT * FROM members WHERE account_number = %s", (account_number,))
        member_details = cur.fetchone()
        cur.close()
    except Exception as e:
        return jsonify({"error": f"Failed to fetch member details: {str(e)}"}), 500

    if not member_details:
        return jsonify({"error": "No member details found."}), 404

    if recipient:
        subject = "Credisync - Loan Application Declined"
        app_name = "CREDISYNC"
        
        # Get the path to the email template
        html_file_path = os.path.join('templates', 'declined-email.html')

        # Get the current date and time 
        current_date = datetime.now().strftime('%Y-%m-%d')

        # Read the HTML content
        try:
            with open(html_file_path, 'r') as file:
                html_content = file.read()

                # Replace placeholders with actual values from database
                html_content = html_content.replace("[SUBJECT HERE]", subject)
                html_content = html_content.replace("[COOPERATIVE NAME]", str(member_details.get('cooperative_name', 'N/A')))
                html_content = html_content.replace("[DATE_DECLINED]", current_date)
                html_content = html_content.replace("[ACCOUNT NUMBER]", str(member_details.get('account_number', 'N/A')))
                html_content = html_content.replace("[APPLICANT NAME]", str(member_details.get('name', 'N/A')))
                html_content = html_content.replace("[APPLICATION DATE]", str(member_details.get('date_applied', 'N/A')))
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
                html_content = html_content.replace("[COOPERATIVE NAME]", str(evaluation_details.get('cooperative_name', 'N/A')))
                html_content = html_content.replace("[DATE_APPROVED]", current_date)
                html_content = html_content.replace("[ACCOUNT NUMBER]", str(evaluation_details.get('account_number', 'N/A')))
                html_content = html_content.replace("[APPLICANT NAME]", evaluation_details.get('firstname', 'N/A'))
                html_content = html_content.replace("[APPLICATION DATE]", str(evaluation_details.get('application_date', 'N/A')))
                html_content = html_content.replace("[EVALUATION DATE]", str(evaluation_details.get('date_evaluated', 'N/A')))
                # loan applicant details
                html_content = html_content.replace("[MONTHLY EARNINGS]", str(evaluation_details.get('monthly_earnings', 'N/A')))
                html_content = html_content.replace("[LOAN TYPE]", str(evaluation_details.get('loan_type', 'N/A')))
                html_content = html_content.replace("[LOAN TERM]", str(evaluation_details.get('loan_term', 'N/A')))
                html_content = html_content.replace("[CO-MAKER]", str(evaluation_details.get('co_maker', 'N/A')))
                html_content = html_content.replace("[SAVINGS ACCOUNT]", str(evaluation_details.get('savings_account', 'N/A')))
                html_content = html_content.replace("[ASSET OWNER]", str(evaluation_details.get('asset_owner', 'N/A')))
                html_content = html_content.replace("[PAYMENT METHOD]", str(evaluation_details.get('payment_method', 'N/A')))
                html_content = html_content.replace("[REPAYMENT SCHEDULE]", str(evaluation_details.get('repayment_schedule', 'N/A')))
                html_content = html_content.replace("[PAYMENT HISTORY]", str(evaluation_details.get('payment_history', 'N/A')))
                #results of evaluation
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


# Route to update member information
@app.route('/update_member_status', methods=['POST'])
def update_member_status():
    data = request.json
    account_number = data.get('account_number')  # Account number is read-only
    status = data.get('status') # for members table
    loan_status = data.get('loan_status') #for loan applications table
    email = data.get('email')  # Include this in checking

    if not account_number or not loan_status:
        return jsonify({"error": "Account number or status not provided"}), 400

    coop_id = session.get('cooperative_id')  # Get cooperative_id from session
    cur = mysql.connection.cursor()

    try:
        # Check if email exists (excluding the current member and within the same cooperative)
        cur.execute("SELECT * FROM loan_applications WHERE email = %s AND account_number != %s AND cooperative_id = %s", (email, account_number, coop_id))
        email_exists = cur.fetchone()

        if email_exists:
            return jsonify({"error": "Email already exists for another account within the same cooperative"}), 409

        # Update the member's status (within the same cooperative)
        cur.execute("UPDATE members SET status = %s WHERE account_number = %s AND cooperative_id = %s", (status, account_number, coop_id))
        cur.execute("UPDATE loan_applications SET loan_status = %s WHERE account_number = %s AND cooperative_id = %s", (loan_status, account_number, coop_id))
        mysql.connection.commit()

        return jsonify({"success": True}), 200
    except Exception as e:
        mysql.connection.rollback()  # Rollback in case of error
        return jsonify({"error": str(e)}), 500
    finally:
        cur.close()


#Cooperative Profile route
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

# Member Profile route
@app.route('/profile', methods=['GET', 'POST'])
def profile():
    account_number = session.get('account_number')
    if not account_number:
        return redirect(url_for('memberlogin'))

    if request.method == 'POST':
        try:
            # Get data from the form submission
            data = request.get_json()
            firstname = data['firstname']
            lastname = data['lastname']
            email = data['email']
            status = data['status']

            cur = mysql.connection.cursor()
            cur.execute("""
                UPDATE members
                SET firstname = %s, lastname = %s, email = %s, status = %s
                WHERE account_number = %s
            """, (firstname, lastname, email, status, account_number))
            mysql.connection.commit()
            cur.close()

             # Update session variables for immediate reflection in the sidebar
            session['firstname'] = firstname
            session['lastname'] = lastname
            session['email'] = email

            return jsonify({"message": "Member profile updated successfully!"}), 200
        except Exception as e:
            mysql.connection.rollback()
            return jsonify({"error": str(e)}), 500
    else:
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT account_number, firstname, lastname, email, status, cooperative_id
            FROM members
            WHERE account_number = %s
        """, (account_number,))
        member = cur.fetchone()
        cur.close()
        if member:
            session['firstname'] = member['firstname']
            session['lastname'] = member['lastname']
            session['email'] = member['email']
            return render_template('profile.html', member=member)
        return jsonify({"error": "Member not found"}), 404

#Evaluation Route
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
                cur.execute("SELECT * FROM loan_applications WHERE account_number = %s", (account_number,))
                loan_applicant = cur.fetchone()

                cur.execute("SELECT * FROM members WHERE account_number = %s", (account_number,))
                member = cur.fetchone()

                if not member:
                    return jsonify({"error": "Member not found"}), 404
                
                # Fetch and calculate all necessary fields
                # Payment History
                cur.execute("""
                    SELECT 
                        CASE 
                            WHEN COUNT(*) = 0 THEN 'No History'
                            WHEN MAX(STR_TO_DATE(payment_date, '%%Y-%%m-%%d')) > MAX(due_date) THEN 'After the due date'
                            ELSE 'On or before the due date'
                        END AS payment_history
                    FROM payments_info
                    WHERE account_number = %s
                """, (account_number,))
                payment_history = cur.fetchone()['payment_history']


                # Monthly Earnings
                cur.execute("""
                    SELECT 
                        CASE 
                            WHEN net_take_home_salary < 11300 THEN 'P11,300 below'
                            WHEN net_take_home_salary BETWEEN 11301 AND 41299 THEN 'P11,301 to P41,299'
                            ELSE 'P41,300 above'
                        END AS monthly_earnings
                    FROM loan_applications
                    WHERE account_number = %s
                """, (account_number,))
                monthly_earnings = cur.fetchone()['monthly_earnings']

                # Loan Type
                cur.execute("""
                    SELECT loan_type FROM loan_applications WHERE account_number = %s
                """, (account_number,))
                loan_type = cur.fetchone()['loan_type']

                # Loan Term
                cur.execute("""
                    SELECT 
                        CASE 
                            WHEN loan_term >= 85 THEN '85 months above'
                            WHEN loan_term BETWEEN 60 AND 84 THEN '60 to 84 months'
                            ELSE '12 to 60 months'
                        END AS loan_term
                    FROM loan_applications
                    WHERE account_number = %s
                """, (account_number,))
                loan_term = cur.fetchone()['loan_term']

                # Co-Maker
                cur.execute("""
                    SELECT 
                        CASE 
                            WHEN COUNT(*) = 0 THEN 'No co-maker'
                            WHEN COUNT(*) BETWEEN 1 AND 2 THEN 'Co-maker with moderate reliability'
                            ELSE 'Co-maker with strong reliability'
                        END AS co_maker_status
                    FROM co_makers_info
                    WHERE account_number = %s
                """, (account_number,))
                co_maker_status = cur.fetchone()['co_maker_status']

                # Fetch Savings Account Status Based on Last Transaction Date
                cur.execute("""
                    SELECT 
                        CASE 
                            WHEN MAX(last_transaction_date) IS NULL THEN 'No Savings Account'
                            WHEN MAX(last_transaction_date) < DATE_SUB(CURDATE(), INTERVAL 1 YEAR) THEN 'Not Active'
                            ELSE 'Active'
                        END AS savings_status
                    FROM savings_account_info
                    WHERE account_number = %s
                """, (account_number,))
                savings_status_row = cur.fetchone()

                # If no row is found, default to 'No Savings Account'
                savings_status = savings_status_row['savings_status'] if savings_status_row else 'No Savings Account'

                # Asset Owner
                cur.execute("""
                    SELECT 
                        CASE 
                            WHEN COUNT(*) = 0 THEN 'No assets'
                            WHEN COUNT(DISTINCT asset_type) = 1 THEN 'Owns properties/vehicle'
                            ELSE 'Owns both properties and vehicle'
                        END AS asset_status
                    FROM assets_info
                    WHERE account_number = %s
                """, (account_number,))
                asset_status = cur.fetchone()['asset_status']

                # Payment Method
                cur.execute("""
                    SELECT payment_method FROM loan_applications WHERE account_number = %s
                """, (account_number,))
                payment_method = cur.fetchone()['payment_method']

                # Repayment Schedule
                cur.execute("""
                    SELECT repayment_schedule FROM loan_applications WHERE account_number = %s
                """, (account_number,))
                repayment_schedule = cur.fetchone()['repayment_schedule']

                # Prepare data for the template
                evaluation_data = {
                    'payment_history': payment_history,
                    'monthly_earnings': monthly_earnings,
                    'loan_type': loan_type,
                    'loan_term': loan_term,
                    'co_maker_status': co_maker_status,
                    'savings_status': savings_status,
                    'asset_status': asset_status,
                    'payment_method': payment_method,
                    'repayment_schedule': repayment_schedule,
                }

                return render_template('evaluation.html', member=member, loan_applicant=loan_applicant, evaluation_data=evaluation_data, cooperative_name=cooperative_name)
                # return render_template('evaluation.html', member=member, )

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
            
            # map values to store plain text in database (evaluated_members table)
            monthly_earnings_map = {
                "50": "P11,300 below",
                "80": "P11,301 to P41,299",
                "100": "P41,300 above"
            }
            loan_type_map = {
                "50": "Personal Loans/Home Equity Loans",
                "80": "Auto Loans/Student Loans",
                "100": "Mortgages/Small Business Loans"
            }
            loan_term_map = {
                "50": "85 months above",
                "80": "60 to 84 months",
                "100": "12 to 60 months"
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
                "50": "Quarterly/Semi-Anually/Anually",
                "80": "Monthly",
                "100": "Weekly"
            }
            payment_history_map = {
                "50": "No History",
                "80": "After the due date",
                "100": "On or before e the due date"
            }

            monthly_earnings = monthly_earnings_map.get(form_data.get('Monthly_Earnings'), '')
            loan_type = loan_type_map.get(form_data.get('Loan_Type'), '')
            loan_term = loan_term_map.get(form_data.get('Loan_Term'), '')
            co_maker = co_maker_map.get(form_data.get('Co_Maker'), '')
            savings_account = savings_account_map.get(form_data.get('Savings_Account'), '')
            asset_owner = asset_owner_map.get(form_data.get('Asset_Owner'), '')
            payment_method = payment_method_map.get(form_data.get('Payment_Method'), '')
            repayment_schedule = repayment_schedule_map.get(form_data.get('Repayment_Schedule'), '')
            payment_history = payment_history_map.get(form_data.get('Payment_History'), '')

            # Get the credit score
            credit_score = int(form_data.get('Credit_Score', 0))

            # Log the form data to inspect the values
            app.logger.info("Received form data:")
            for key, value in form_data.items():
                app.logger.info(f"{key}: {value}")

            required_fields = [
                'Monthly_Earnings', 'Loan_Type', 'Loan_Term',
                'Co_Maker', 'Savings_Account', 'Asset_Owner',
                'Payment_Method', 'Repayment_Schedule', 'Payment_History','Credit_Score'
            ]

            # missing_fields = [field for field in required_fields if not form_data.get(field)]
            missing_fields = [field for field in required_fields if form_data.get(field) is None]
            if missing_fields:
                app.logger.error(f"Missing fields: {missing_fields}")
                return jsonify({"error": f"Missing required fields: {', '.join(missing_fields)}"}), 400

            features = [
                # float(form_data.get('Monthly_Earnings')),
                float(form_data.get('Monthly_Earnings', 0)),
                float(form_data.get('Loan_Type', 0)),
                float(form_data.get('Loan_Term', 0)),
                float(form_data.get('Co_Maker', 0)),
                float(form_data.get('Savings_Account', 0)),
                float(form_data.get('Asset_Owner', 0)),
                float(form_data.get('Payment_Method', 0)),
                float(form_data.get('Repayment_Schedule', 0)),
                float(form_data.get('Payment_History', 0)),
                float(form_data.get('Credit_Score', 0))
            ]

            features_array = np.array([features])

            # Assuming you have a pre-loaded model
            eligibility_prediction = ELIGIBILITY_MODEL.predict(features_array)[0]
            eligibility_text = 'Eligible for a loan' if eligibility_prediction == 1 else 'Not eligible for a loan'

            app.logger.info(f"Prediction result - Eligibility: {eligibility_text}")

             # Get the current date as the evaluation date
            datetime.now().strftime('%Y-%m-%d')

             # Save evaluation details to the evaluated_members table
            firstname = form_data.get('firstname')
            contact_number = form_data.get('contact_number')
            email = form_data.get('email')
            present_address = form_data.get('present_address')
            application_date = form_data.get('application_date')

            #  # evaluation details
           
            # monthly_earnings = form_data.get('Monthly_Earnings')
            # loan_type = form_data.get('Loan_Type')
            # loan_term = form_data.get('Loan_Term')
            # co_maker = form_data.get('Co_Maker')
            # savings_account = form_data.get('Savings_Account')
            # asset_owner = form_data.get('Asset_Owner')
            # payment_method = form_data.get('Payment_Method')
            # repayment_schedule = form_data.get('Repayment_Schedule')
            # payment_history = form_data.get('Payment_History') #this is Payment History field in the eval form

            cur = mysql.connection.cursor()

            try:
                # save to evaluated_members table
                cur.execute("""
                    INSERT INTO evaluated_members (
                        account_number, firstname, contact_number, email, present_address, application_date, status, credit_score, 
                        prediction, date_evaluated, monthly_earnings, loan_type, loan_term, co_maker, 
                        savings_account, asset_owner, payment_method, repayment_schedule, payment_history, cooperative_id, cooperative_name
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    account_number, form_data.get('firstname'), form_data.get('contact_number'), form_data.get('email'),
                    form_data.get('present_address'), form_data.get('application_date'), 'Evaluated', 
                    credit_score, eligibility_text, datetime.now().strftime('%Y-%m-%d'), 
                    monthly_earnings, loan_type, loan_term, 
                    co_maker, savings_account, asset_owner, 
                    payment_method, repayment_schedule, payment_history, cooperative_id, cooperative_name
                ))

                # Commit the changes
                mysql.connection.commit()

                # Now, update the member's status in the original members table and loan_applications table
                cur.execute("UPDATE members SET status = 'Evaluated' WHERE account_number = %s", (account_number,))
                mysql.connection.commit()

                cur.execute("UPDATE loan_applications SET loan_status = 'Evaluated' WHERE account_number = %s", (account_number,))
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
        cur.execute("""
            SELECT * FROM loan_applications WHERE account_number = %s
        """, (account_number,))
        member = cur.fetchone()

        # Close cursor
        cur.close()

        success_message = session.pop('success', None)  # Get success message if available

        if member:
            return render_template(
                'member-profile.html', 
                member=member, 
                success=success_message, 
                cooperative_name=cooperative_name, 
             )
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
