from flask import Flask, render_template, request, jsonify, session, g, redirect, url_for
from werkzeug.security import generate_password_hash
import bcrypt
# from flask_mail import Mail
from flask_mysqldb import MySQL 
from flask_mail import Mail
from flask_mysqldb import MySQL
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

# Before request to check if user is logged in but allow access to signup
@app.before_request 
def before_request(): 
    g.user = None 
    if 'user_id' in session: 
        g.user = session['user_id']
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

        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM user WHERE cooperative_id = %s', (cooperative_id,))
        user = cursor.fetchone()
        cursor.close()

        if user:
            stored_password = user['password'].encode('utf-8')
            entered_password = password.encode('utf-8')

            # Debugging logs
            print(f"Stored Password: {stored_password}")
            print(f"Entered Password: {entered_password}")

            if bcrypt.checkpw(entered_password, stored_password):
                session.pop('error', None)  # Clear any previous error messages
                session['user_id'] = user['cooperative_id']
                return redirect(url_for('dashboard'))
            else:
                session['error'] = 'Invalid credentials. Please try again.'
                return redirect(url_for('login'))
        else:
            session['error'] = 'Invalid credentials. Please try again.'
            return redirect(url_for('login'))
    success_message = session.pop('success', None) # Get success message if available
    error_message = session.pop('error', None) #if entered wrong credentials
    return render_template('login.html', success=success_message, error=error_message)

# Logout route
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))

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

        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        try:
            cursor.execute('INSERT INTO user (cooperative_id, password, cooperative_name, address, contact_number) VALUES (%s, %s, %s, %s, %s)',
                           (cooperative_id, hashed_password.decode('utf-8'), cooperative_name, address, contact_number))
            mysql.connection.commit()
            session.pop('error', None)  # Clear any previous error messages
            session['success'] = 'User account successfully created!'
            cursor.close()
            return redirect(url_for('login'))
        except Exception as e:
            session['error'] = str(e)
            cursor.close()
            return redirect(url_for('signup'))

    return render_template('signup.html')

# Dashboard route
@app.route('/', methods=['GET'])
def dashboard():
    if not g.user:
        return redirect(url_for('login'))
    subscriptions = load_subscriptions()
    return render_template('dashboard.html', subscriptions=subscriptions)

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

# Members route cooperative end
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
            cur.execute("INSERT INTO members (account_number, name, contact_number, email, address, date_applied, status) VALUES (%s, %s, %s, %s, %s, %s, 'Pending')", (account_number, name, contact_number, email, address, date_applied))
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


# Declined  members route
@app.route('/decline_member', methods=['POST'])
def decline_member():
    # decline using account number
    account_number = request.json.get('account_number')

    if not account_number:
        return jsonify({"error": "Account number not provided"}), 400

    cur = mysql.connection.cursor() 

    try:
        # Retrieve the member details didto sa members table gamit ang account number gikan html
        cur.execute("SELECT * FROM members WHERE account_number = %s", (account_number,))
        member = cur.fetchone()

        if not member:
            return jsonify({"error": "Member not found"}), 404

         # Update the member's status to 'Declined' in members table
        cur.execute("UPDATE members SET status = 'Declined' WHERE account_number = %s", (account_number,))

        # Insert the declined member into declined_members table
        cur.execute("INSERT INTO declined_members (account_number, name, contact_number, email, address, date_applied, status) VALUES (%s, %s, %s, %s, %s, %s, 'Declined')",
                    (member['account_number'], member['name'], member['contact_number'], member['email'], member['address'], member['date_applied']))

        # Delete the member from the members table pero no need for now since we want to countnumber of rows in members para display in dashboard
        # cur.execute("DELETE FROM members WHERE account_number = %s", (account_number,))
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
    recipient = request.json.get('recipient')  # Extract the recipient gikan sa members html
    applicant_name = request.json.get('applicantName')  # Get the applicant's name
    if recipient:
        subject = "Credisync - Loan Application Approved"
        app_name = "CREDISYNC"

         # Get the path sa html email content mao ni ma display sa email 
        html_file_path = os.path.join('templates', 'email.html')

        # Read the HTML content
        try:
            with open(html_file_path, 'r') as file:
                html_content = file.read()
                # Replace placeholders with actual values
                html_content = html_content.replace("[SUBJECT HERE]", subject)
                html_content = html_content.replace("[BODY HERE]", f"Dear {applicant_name}, we are pleased to inform you that your credisync loan application has been approved.")
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


# Route to update member loan application status
@app.route('/update_member_status', methods=['POST'])
def update_member_status():
    data = request.json
    account_number = data.get('account_number')
    status = data.get('status')

    if not account_number or not status:
        return jsonify({"error": "Account number or status not provided"}), 400

    cur = mysql.connection.cursor()

    try:
        # Update the member's status
        cur.execute("UPDATE members SET status = %s WHERE account_number = %s", (status, account_number))
        mysql.connection.commit()

        return jsonify({"success": True}), 200
    except Exception as e:
        mysql.connection.rollback()  # Rollback in case of error
        return jsonify({"error": str(e)}), 500
    finally:
        cur.close()

# # Route to fetch the status of all members
# @app.route('/get_member_statuses', methods=['GET'])
# def get_member_statuses():
#     cur = mysql.connection.cursor()

#     try:
#         # Fetch all members and their status from the database
#         cur.execute("SELECT account_number, name, email, status FROM members")
#         members = cur.fetchall()

#         return jsonify({"members": members}), 200
#     except Exception as e:
#         cur.close()
#         return jsonify({"error": str(e)}), 500

# Settings page
@app.route('/settings', methods=['GET', 'POST'])
def settings():
    if request.method == 'POST':
        # Handle form submission
        coop_name = request.form['coopName']
        coop_shortName = request.form['coopShortName']
        address = request.form['address']
        contact_number = request.form['contactNumber']
        email = request.form['email']

        cur = mysql.connection.cursor()
        try:
            cur.execute("""
                UPDATE user
                SET coop_name = %s, coop_shortName = %s, address = %s, contact_number = %s, email = %s
                LIMIT 1
            """, (coop_name, coop_shortName, address, contact_number, email))
            mysql.connection.commit()
        except Exception as e:
            mysql.connection.rollback()
            return f"Error updating user: {str(e)}", 500
        finally:
            cur.close()
        return redirect(url_for('settings'))
    else:
        # Initial data fetching is handled by the get_user endpoint via AJAX
        return render_template('settings.html')

@app.route('/get_user', methods=['GET'])
def get_user():
    cur = mysql.connection.cursor()
    try:
        cur.execute("SELECT coop_name, coop_shortName, address, contact_number, email FROM user LIMIT 1")
        user = cur.fetchone()

        if not user:
            return jsonify({"error": "User not found"}), 404

        user_data = {
            "coop_name": user[0],
            "coop_shortName": user[1],
            "address": user[2],
            "contact_number": user[3],
            "email": user[4]
        }
        return jsonify(user_data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cur.close()

# # Evaluation page
# @app.route('/evaluation', methods=['GET', 'POST'])
# def evaluation():
#     try:
#         # Handling GET request: Display member info
#         if request.method == 'GET':
#             account_number = request.args.get('account_number')

#             if not account_number:
#                 return jsonify({"error": "Account number not provided"}), 400  # Handle the case where no account_number is passed

#             # Get member data from DB
#             cur = mysql.connection.cursor()

#             try:
#                 # Query to get the member data by account_number
#                 cur.execute("SELECT * FROM members WHERE account_number = %s", (account_number,))
#                 member = cur.fetchone()

#                 # If member doesn't exist, return a 404 error
#                 if not member:
#                     return jsonify({"error": "Member not found"}), 404

#                 # Render the evaluation page with member data
#                 return render_template('evaluation.html', member=member)

#             except Exception as e:
#                 app.logger.error(f"Database error: {str(e)}")
#                 return jsonify({"error": "Error fetching member data"}), 500
#             finally:
#                 cur.close()

#         # Handling POST request: Perform prediction based on form data
#         elif request.method == 'POST':
#             form_data = request.form

#             # Validate inputs
#             required_fields = [
#                 'payment_history_score', 'monthly_salary_score', 'loan_term_score',
#                 'co_maker_score', 'savings_account_score', 'asset_owner_score',
#                 'payment_method_score', 'repayment_schedule_score', 'credit_score'
#             ]
#             missing_fields = [field for field in required_fields if not form_data.get(field)]
#             if missing_fields:
#                 return jsonify({"error": f"Missing required form data: {', '.join(missing_fields)}"}), 400

#             # Map form data to numerical features for the model
#             features = [
#                 float(form_data.get('payment_history_score')),
#                 float(form_data.get('monthly_salary_score')),
#                 float(form_data.get('loan_term_score')),
#                 float(form_data.get('co_maker_score')),
#                 float(form_data.get('savings_account_score')),
#                 float(form_data.get('asset_owner_score')),
#                 float(form_data.get('payment_method_score')),
#                 float(form_data.get('repayment_schedule_score')),
#                 float(form_data.get('credit_score'))
#             ]

#             features_array = np.array([features])

#             # Predict eligibility using the pre-loaded model
#             eligibility_prediction = ELIGIBILITY_MODEL.predict(features_array)[0]

#             # Convert eligibility prediction to human-readable text
#             eligibility_text = 'Eligible' if eligibility_prediction == 1 else 'Not eligible'

#             # Log the result (for debugging purposes)
#             app.logger.info(f"Prediction result - Eligibility: {eligibility_text}")

#             # Return prediction result as JSON response
#             return jsonify({
#                 'eligibility': eligibility_text
#             })

#     except Exception as e:
#         # Log any unexpected errors
#         app.logger.error(f"Unexpected error: {str(e)}")
#         return jsonify({"error": "Internal server error"}), 500

    
@app.route('/evaluation', methods=['GET'])
def evaluation():
    # Get the account_number from the query parameters
    account_number = request.args.get('account_number')

    if not account_number:
        return "Account number not provided", 400  # Handle the case where no account_number is passed

    # Create a cursor and try to fetch the member data by account_number
    cur = mysql.connection.cursor()
    try:
        # Query to get the member data by account_number
        cur.execute("SELECT * FROM members WHERE account_number = %s", (account_number,))
        member = cur.fetchone()

        # If member doesn't exist, return a 404 or similar error
        if not member:
            return "Member not found", 404

        # Render the evaluation page with member data
        return render_template('evaluation.html', member=member)

    except Exception as e:
        print(f"Error fetching member: {e}")
        return "Error fetching member data", 500
    finally:
        cur.close()


# Member profile page 
@app.route('/member-profile/<account_number>')
def member_profile(account_number):
    cur = mysql.connection.cursor()
    try:
        # Fetch member details based on account number
        cur.execute("SELECT * FROM members WHERE account_number = %s", (account_number,))
        member = cur.fetchone()

        # Close cursor
        cur.close()

        if member:
            return render_template('member-profile.html', member=member)
        else:
            return "Member not found", 404

    except Exception as e:
        cur.close()
        return jsonify({"error": str(e)}), 500

# display 404 html
@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404

if __name__ == "__main__":
    app.run(debug=True)

# if __name__ == "__main__":
# app.run(debug=True, host='0.0.0.0')
