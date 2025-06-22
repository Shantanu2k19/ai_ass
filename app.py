from flask import Flask, render_template, request, redirect, session, url_for, jsonify, abort
from werkzeug.security import check_password_hash
from dotenv import load_dotenv
import os
import requests

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

FEEDS = {
    "light1": "relay-group.relay-1",
    "strip_lights":"actions.lights-off"
}

ADAFRUIT_USERNAME = os.getenv("ADA_USERNAME")
AIO_KEY = os.getenv("AIO_KEY")
FEED_URL = f"https://io.adafruit.com/api/v2/{ADAFRUIT_USERNAME}/feeds/relay-group.relay-1"



### ROUTES ####

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
    
    statuses = {}
    for key in FEEDS:
        statuses[key] = get_feed_value(key)
    print(f"got statuses: {statuses}")
    return render_template('dashboard.html', statuses = statuses)

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')


### AJAX ####

@app.route('/toggle/<device>', methods=['POST'])
def toggle_device(device):
    if 'user' not in session:
        return abort(403)
    if device not in FEEDS:
        return abort(400)

    data = request.get_json()
    value = data.get("status").upper()
    print(f"status: {value}")
    success = set_feed_value(device, value)
    return jsonify({ "success": success })


### UTILITY FUNCTIONS ####

def set_feed_value(feed_key, value):
    feed_name = FEEDS.get(feed_key)
    if not feed_name:
        return False
    url = f"https://io.adafruit.com/api/v2/{ADAFRUIT_USERNAME}/feeds/{feed_name}/data"
    headers = {
        "X-AIO-Key": AIO_KEY,
        "Content-Type": "application/json"
    }
    res = requests.post(url, headers=headers, json={"value": str(value)})
    return res.ok

def get_feed_value(feed_key):
    feed_name = FEEDS[feed_key]
    url = f"https://io.adafruit.com/api/v2/{ADAFRUIT_USERNAME}/feeds/{feed_name}/data/last"
    headers = {"X-AIO-Key": AIO_KEY}
    response = requests.get(url, headers=headers)
    if response.ok:
        return response.json().get("value") == "ON"
    return False

def set_feed_value(feed_key, value):
    feed_name = FEEDS[feed_key]
    url = f"https://io.adafruit.com/api/v2/{ADAFRUIT_USERNAME}/feeds/{feed_name}/data"
    headers = {"X-AIO-Key": AIO_KEY, "Content-Type": "application/json"}
    response = requests.post(url, headers=headers, json={"value": str(value)})
    return response.ok


### MAIN ####

if __name__ == '__main__':
    app.run(debug=True)
