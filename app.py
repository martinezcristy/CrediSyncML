from flask import Flask, render_template, request, redirect, url_for
#from flask_mysqldb import MYSQL

#from flask_mail import Mail, Message
# from dotenv import load_dotenv
# import os
# load_dotenv()

# Create a Blueprint sa email api file
# email_blueprint = Blueprint('email_api', __name__)

# declare og variables para sa email api (values from env)
# EMAIL_SERVER_NI_SHA = os.getenv("MAIL_SERVER")
# EMAIL_PORT_NI_SHA = os.getenv("MAIL_PORT")
# EMAIL_USE_TLS_NI = os.getenv("MAIL_USE_TLS")
# EMAIL_USERNAME = os.getenv("MAIL_USERNAME")
# EMAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
# EMAIL_SENDER_CREDISYNC = os.getenv("MAIL_DEFAULT_SENDER")

app = Flask(__name__) 

# Mail configuration
# app.config['MAIL_SERVER'] = EMAIL_SERVER_NI_SHA
# app.config['MAIL_PORT'] = EMAIL_PORT_NI_SHA
# app.config['MAIL_USE_TLS'] = EMAIL_USE_TLS_NI
# app.config['MAIL_USERNAME'] = EMAIL_USERNAME
# app.config['MAIL_PASSWORD'] = EMAIL_PASSWORD
# app.config['MAIL_DEFAULT_SENDER'] = EMAIL_SENDER_CREDISYNC

#mysql configuration
# app.config['MYSQL_HOST'] = 'localhost'
# app.config['MYSQL_USER'] = 'root'
# app.config['MYSQL_PASSWORD'] = ""
# app.config['MYSQL_DB'] = ['credisync_db']

# mysql = MYSQL(app)

#dashboard routes
@app.route('/', methods=['GET'])
def dashboard():
    return render_template('dashboard.html')

#members route
@app.route('/members', methods=['GET', 'POST'])
def members():
    #SQL LOGIC
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