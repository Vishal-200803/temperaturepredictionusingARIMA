import pandas as pd
import os
import pickle
from flask import Flask, render_template, request, redirect, url_for, session

application = Flask(__name__)

# Use a secret key for session management
application.secret_key = 'your_secret_key'

# Check if users.csv file exists, and create it if not
if not os.path.isfile('users.csv'):
    with open('users.csv', 'w') as file:
        pass

@application.route('/')
def home_page():
    # Check if the user is logged in using the session
    if 'username' in session:
        return render_template('home.html')
    else:
        # If the user is not logged in, redirect to the login page
        return redirect(url_for('login'))

@application.route('/pred', methods=['GET', 'POST'])
def predict_temp():
    if request.method == 'GET':
        return render_template('form.html')
    else:
        start_date = pd.to_datetime(request.form['start_date'])
        end_date = pd.to_datetime(request.form['end_date'])

        with open(r'./model.pkl', 'rb') as f:
            model = pickle.load(f)

        model_last_date = pd.to_datetime("2019-12-30")

        d1 = (start_date - model_last_date).days

        days_diff = (end_date - start_date).days

        pred = model.predict(start=1821 + d1, end=1821 + d1 + days_diff, typ='levels').rename('ARIMA PREDICTIONS')
        index_future_dates = pd.date_range(start=start_date, end=end_date)

        pred.index = index_future_dates.strftime('%Y-%m-%d')
        return render_template('result.html', predictions=pred, start_date=start_date.strftime('%Y-%m-%d'),
                               end_date=end_date.strftime('%Y-%m-%d'))

@application.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Replace with your own logic for user verification
        if verify_user(username, password):
            session['username'] = username  # Store the username in the session
            return redirect(url_for('home_page'))  # Redirect to home.html on successful login
        else:
            return "Login failed. <a href='/login'>Try again</a>"

    return render_template('login.html')

@application.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Replace with your own logic for user registration
        if register_user(username, password):
            session['username'] = username  # Store the username in the session
            return redirect(url_for('home_page'))  # Redirect to home.html on successful signup
        else:
            return "Registration failed. <a href='/signup'>Try again</a>"

    return render_template('signup.html')

# Replace this with your own user verification logic
def verify_user(username, password):
    # Load user data from CSV file and check for a match
    with open('users.csv', 'r') as file:
        for line in file:
            stored_username, stored_password = line.strip().split(',')
            if username == stored_username and password == stored_password:
                return True
    return False

# Replace this with your own user registration logic
def register_user(username, password):
    # Check if the username already exists
    with open('users.csv', 'r') as file:
        for line in file:
            stored_username, _ = line.strip().split(',')
            if username == stored_username:
                return False

    # If the username is unique, add it to the CSV file
    with open('users.csv', 'a') as file:
        file.write(f'{username},{password}\n')
    return True

if __name__ == "__main__":
    application.run(host='0.0.0.0', debug=True)
