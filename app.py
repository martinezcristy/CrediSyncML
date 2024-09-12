from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def members():
    return render_template('members.html')

if __name__ == "__main__":
    app.run(debug=True)
