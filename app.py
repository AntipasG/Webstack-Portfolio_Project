from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import json
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with your secret key

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'signin'

PASSWORD_FILE = "data.txt"
USERS_FILE = "users.txt"

# Load and save functions
def load_passwords():
    if os.path.exists(PASSWORD_FILE):
        with open(PASSWORD_FILE, 'r') as file:
            return json.load(file)
    return []

def save_passwords(passwords):
    with open(PASSWORD_FILE, 'w') as file:
        json.dump(passwords, file, indent=4)

def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r') as file:
            return json.load(file)
    return []

def save_users(users):
    with open(USERS_FILE, 'w') as file:
        json.dump(users, file, indent=4)

# User class for Flask-Login
class User(UserMixin):
    def __init__(self, id):
        self.id = id

@login_manager.user_loader
def load_user(user_id):
    users = load_users()
    for user in users:
        if user['id'] == user_id:
            return User(user_id)
    return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if username and password:
            users = load_users()
            for user in users:
                if user['username'] == username:
                    flash('Username already exists.', 'error')
                    return redirect(url_for('signup'))
            
            hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
            users.append({'id': str(len(users) + 1), 'username': username, 'password': hashed_password})
            save_users(users)
            flash('Signup successful! Please signin.', 'success')
            return redirect(url_for('signin'))
        else:
            flash('Please fill out all fields.', 'error')
    
    return render_template('signup.html')

@app.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if username and password:
            users = load_users()
            for user in users:
                if user['username'] == username and check_password_hash(user['password'], password):
                    user_obj = User(user['id'])
                    login_user(user_obj)
                    flash('Signin successful!', 'success')
                    return redirect(url_for('index'))
            flash('Invalid username or password.', 'error')
        else:
            flash('Please fill out all fields.', 'error')
    
    return render_template('signin.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('index'))

@app.route('/add', methods=['GET', 'POST'])
@login_required
def add_password():
    if request.method == 'POST':
        website = request.form['website']
        email = request.form['email']
        password = request.form['password']
        
        if website and email and password:
            passwords = load_passwords()
            passwords.append({'website': website, 'email': email, 'password': password})
            save_passwords(passwords)
            flash('Password saved successfully!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Please fill out all fields.', 'error')
    
    return render_template('add_password.html')

@app.route('/passwords')
@login_required
def display_passwords():
    passwords = load_passwords()
    return render_template('display_passwords.html', passwords=passwords)

@app.route('/delete/<int:index>', methods=['POST'])
@login_required
def delete_password(index):
    passwords = load_passwords()
    if 0 <= index < len(passwords):
        passwords.pop(index)
        save_passwords(passwords)
        flash('Password deleted successfully!', 'success')
    else:
        flash('Invalid password index.', 'error')
    return redirect(url_for('display_passwords'))
@app.route('/delete_account', methods=['POST'])
@login_required
def delete_account():
    users = load_users()
    passwords = load_passwords()

    # Remove user from users list
    updated_users = [user for user in users if user['id'] != current_user.id]
    save_users(updated_users)

    # Remove passwords associated with the user
    updated_passwords = [password for password in passwords if password['user_id'] != current_user.id]
    save_passwords(updated_passwords)

    logout_user()
    flash('Account deleted successfully.', 'success')
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)
