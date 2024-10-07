from flask import Flask, render_template, request, redirect, url_for
#from flask_mysqldb import MySQL
from flask_mysqldb import MySQL
from models import Member

# from flask_mail import Mail, Message

from dotenv import load_dotenv
import os

load_dotenv()

# Create a Blueprint sa email api file
# email_blueprint = Blueprint('email_api', __name__)

#email api (values from env)
EMAIL_SERVER_NI_SHA = os.getenv("MAIL_SERVER")
EMAIL_PORT_NI_SHA = os.getenv("MAIL_PORT")
EMAIL_USE_TLS_NI = os.getenv("MAIL_USE_TLS")
EMAIL_USERNAME = os.getenv("MAIL_USERNAME")
EMAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
EMAIL_SENDER_CREDISYNC = os.getenv("MAIL_DEFAULT_SENDER")

#sql values from env
MYSQL_HOST = os.getenv('SQL_HOSTNAME')
MYSQL_PORT = os.getenv('SQL_PORT')
MYSQL_USER = os.getenv('SQL_USERNAME')
MYSQL_PASSWORD = os.getenv('SQL_PASSWORD')
MYSQL_DB = os.getenv('SQL_DB')

app = Flask(__name__) 

# Mail configuration
app.config['MAIL_SERVER'] = EMAIL_SERVER_NI_SHA
app.config['MAIL_PORT'] = EMAIL_PORT_NI_SHA
app.config['MAIL_USE_TLS'] = EMAIL_USE_TLS_NI
app.config['MAIL_USERNAME'] = EMAIL_USERNAME
app.config['MAIL_PASSWORD'] = EMAIL_PASSWORD
app.config['MAIL_DEFAULT_SENDER'] = EMAIL_SENDER_CREDISYNC

#mysql configuration
app.config['SQL_HOSTNAME'] = MYSQL_HOST
app.config['SQL_PORT'] = MYSQL_PORT
app.config['SQL_USERNAME'] = MYSQL_USER
app.config['SQL_PASSWORD'] = MYSQL_PASSWORD
app.config['SQL_DB'] = MYSQL_DB

#mysql = MYSQL(app)
members_list = []

#dashboard routes
@app.route('/', methods=['GET'])
def dashboard():
    return render_template('dashboard.html')

# Members route
@app.route('/members', methods=['GET', 'POST'])
def members():
    # if request.method == 'POST':
    #     # Retrieve form data
    #     account_number = request.form['account-number']
    #     name = request.form['name']
    #     contact_number = request.form['contact-number']
    #     email = request.form['email-address']
    #     address = request.form['address']
    #     date_applied = request.form['date-applied']
        
    #     # Create a new member with type hints
    #     new_member = Member(account_number=account_number, name=name, 
    #                         contact_number=contact_number, email=email, 
    #                         address=address, date_applied=date_applied)
        
    #     # Save the member to the database
    #     cur = mysql.connection.cursor()
    #     cur.execute("INSERT INTO members (account_number, name, contact_number, email, address, date_applied) VALUES (%s, %s, %s, %s, %s, %s)",
    #                 (new_member.account_number, new_member.name, new_member.contact_number, 
    #                  new_member.email, new_member.address, new_member.date_applied))
    #     mysql.connection.commit()
    #     cur.close()

    #     # Redirect to the same page to display the updated member list
    #     return redirect(url_for('members'))

    # # For GET request, retrieve members from the database
    # cur = mysql.connection.cursor()
    # cur.execute("SELECT * FROM members")
    # members_data = cur.fetchall()
    # cur.close()

    # # Convert fetched data to Member objects
    # members_list = [Member(*member) for member in members_data]

    # return render_template('members.html', members=members_list)

    return render_template('members.html')

#settings route
@app.route('/settings', methods=['GET', 'POST'])
def settings():
    return render_template('settings.html')

#evaluation route
@app.route('/evaluation')
def evaluation():
    return render_template('evaluation.html')

if __name__ == "__main__":
    app.run(debug=True)