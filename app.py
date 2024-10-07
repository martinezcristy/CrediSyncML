from flask import Flask, render_template, request, redirect, url_for
#import mysql.connector

app = Flask(__name__)

#main route
@app.route('/')
def dashboard():
    return render_template('dashboard.html')

#members route
@app.route('/members', methods=['GET', 'POST'])
def members():
    #sql logic
    return render_template('members.html')

#settings route (edit cooperative profile)
@app.route('/settings')
def settings():
    return render_template('settings.html')

#evaluation route
@app.route('/evaluation')
def evaluation():
    return render_template('evaluation.html')

if __name__ == "__main__":
    app.run(debug=True)