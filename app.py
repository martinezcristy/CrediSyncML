from flask import Flask, render_template, request, redirect, url_for, flash
from flask_mysqldb import MySQL
from models import Member
from dotenv import load_dotenv
import os

load_dotenv()

# SQL values from env
MYSQL_HOST = os.getenv('SQL_HOSTNAME')
MYSQL_USER = os.getenv('SQL_USERNAME')
MYSQL_PASSWORD = os.getenv('SQL_PASSWORD')
MYSQL_DB = os.getenv('SQL_DB')

# Create Flask app instance
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'your_default_secret_key')  # Ensure you have a secret key for session management

#MYSQL CONFIGURATION
app.config['MYSQL_HOST'] = MYSQL_HOST
app.config['MYSQL_USER'] = MYSQL_USER
app.config['MYSQL_PASSWORD'] = MYSQL_PASSWORD
app.config['MYSQL_DB'] = MYSQL_DB
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

# Initialize MySQL
mysql = MySQL(app)

# Dashboard route
@app.route('/', methods=['GET'])
def dashboard():
    return render_template('dashboard.html')

# Members route
@app.route('/members', methods=['GET', 'POST'])
def members():
    if request.method == 'POST':
        # Retrieve form data
        account_number = request.form['account-number']
        name = request.form['name']
        contact_number = request.form['contact-number']
        email = request.form['email-address']
        address = request.form['address']
        date_applied = request.form['date-applied']
        
        # Create a new member with type hints
        # new_member = Member(
        #     account_number=account_number, 
        #     name=name, 
        #     contact_number=contact_number, 
        #     email=email, 
        #     address=address, 
        #     date_applied=date_applied
        # )

        # Save the member to the database
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO members (account_number, name, contact_number, email, address, date_applied) VALUES (%s, %s, %s, %s, %s, %s)", (account_number, name, contact_number, email, address, date_applied))
        mysql.connection.commit()
        cur.close()
            # flash('Member added successfully!', 'success')  # Inform user of successful insertion
        # except Exception as e:
            # print(f"Error inserting member: {e}")  # Print the error to console for debugging
            # flash('An error occurred while adding the member. Please try again.', 'error')  # Inform user of error
            # return redirect(url_for('members'))  

        # return redirect(url_for('members'))
        return render_template('members.html')

    # For GET request, retrieve members from the database
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM members")
    members_data = cur.fetchall()
    cur.close()

    # Convert fetched data to Member objects
    members_list = [Member(**member) for member in members_data]  # Using dictionary unpacking

    return render_template('members.html', members=members_list)

# Settings route
@app.route('/settings', methods=['GET', 'POST'])
def settings():
    return render_template('settings.html')

# Evaluation route
@app.route('/evaluation')
def evaluation():
    return render_template('evaluation.html')

# Decline route
@app.route('/declineMember', methods=['POST'])
def decline():
    return 'test decline'  

# Approve route
@app.route('/approveMember')
def approve():
    return 'test approve'  

if __name__ == "__main__":
    app.run(debug=True)
