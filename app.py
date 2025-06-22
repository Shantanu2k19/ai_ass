from flask import Flask, render_template, request, redirect, session, url_for
from werkzeug.security import check_password_hash
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")


@app.route('/')
def home():
    return redirect('/dashboard') if 'user' in session else redirect('/login')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        env_hash = os.getenv("PASSWORD_HASH")
        if not env_hash:
            return "Hash not found", 401

        username = request.form['username']
        password = request.form['password']

        if (username == os.getenv("USERNAME") and
                check_password_hash(env_hash, password)):
            session['user'] = username
            return redirect('/dashboard')
        
        # Invalid login, show message
        return render_template('login.html', error="Invalid username or password")

    return render_template('login.html')



@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect('/login')
    return render_template('dashboard.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')


if __name__ == '__main__':
    app.run(debug=True)
