from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def dashboard():
    return render_template('dashboard.html')

@app.route('/members')
def members():
    return render_template('members.html')

@app.route('/settings')
def settings():
    return render_template('settings.html')

@app.route('/evaluation')
def evaluation():
    return render_template('evaluation.html')

if __name__ == "__main__":
    app.run(debug=True)
