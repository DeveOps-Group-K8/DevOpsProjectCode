import random
from flask import Flask, render_template, redirect, url_for, request, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
import models
from flask import jsonify
from flask_login import login_required, current_user
from models import User, db

# Initialize Flask App
app = Flask(__name__)

# PostgreSQL Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:9257postgres@localhost/users'
#app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://devuser:devpass@localhost/devopsdb'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'supersecretkey'

# Initialize the database object only once
migrate = Migrate(app, db)
db.init_app(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager()
login_manager.init_app(app)

# Login Manager user_loader function
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Home Page (Landing Page)
@app.route('/')
def home():
    return render_template('index.html')

# Register Page
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Check if user exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash("Username already exists. Try another one!", "danger")
            return redirect(url_for('register'))

        # Store hashed password
        new_user = User(username=username)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        
        flash("Registration Successful!", "success")
        return redirect(url_for('login'))
    
    return render_template('register.html')

# Login Page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Check user credentials
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            # Log the user in using Flask-Login
            login_user(user)  # This will manage the session automatically
            flash(f"Welcome back, {user.username}!", "success")
            return redirect(url_for('dashboard'))  # Redirect to the dashboard
        else:
            flash("Invalid credentials! Try again.", "danger")
    
    return render_template('login.html')

@app.route('/config-check')
def config_check():
    return f"Testing Mode: {app.config['TESTING']}"

@app.route('/user-check')
def user_check():
    if current_user.is_authenticated:
        return f"Logged in as: {current_user.username}"
    else:
        return "No user is currently logged in."

# Dashboard Page
@app.route('/dashboard')
@login_required
def dashboard():
    print(f"[DEBUG] Logged in user: {current_user.username}")
    return render_template('dashboard.html', username=current_user.username)

@app.route('/guess', methods=['POST'])
@login_required
def guess():
    try:
        guess = int(request.form['guess'])
    except ValueError:
        flash("Invalid guess! Please enter a valid number.", "danger")
        return redirect(url_for('play_game', level=session.get('level', 'easy')))
    
    number_to_guess = session.get('number_to_guess')
    
    if guess == number_to_guess:
        current_user.score += 1
        db.session.commit()
        return jsonify({'result': 'Correct! You guessed it!'})
    elif guess < number_to_guess:
        return jsonify({'result': 'Too low!'})
    else:
        return jsonify({'result': 'Too high!'})

# Game Page (Handles Easy, Medium, Hard)
@app.route('/play/<level>', methods=['GET', 'POST'])
@login_required  # This ensures the user is logged in
def play_game(level):
    # Define level ranges
    levels = {'easy': 100, 'medium': 200, 'hard': 500}
    if level not in levels:
        flash("Invalid level selected!", "danger")
        return redirect(url_for('dashboard'))

    # Get the current user
    user = current_user

    # Initialize session variables if they aren't set
    if 'random_number' not in session or 'attempts' not in session or 'game_status' not in session:
        session['random_number'] = random.randint(1, levels[level])
        session['attempts'] = 5  # Total number of attempts
        session['game_status'] = None  # Track the game status (win/loss)
        session['level'] = level  # Store the current level

    # Game variables
    correct_number = session['random_number']
    attempts = session['attempts']
    game_status = session['game_status']  # 'win' or 'loss'

    # Leaderboard fetching
    leaderboard = User.query.order_by(User.score.desc()).limit(10).all()
    leaderboard_dicts = [u.to_dict() for u in leaderboard]

    if request.method == 'POST' and game_status is None:  # Only process guesses if the game isn't over
        # Get the user's guess and ensure it's a valid integer
        guess = request.form.get('guess', type=int)
        
        if guess is None:
            flash("Invalid guess! Please enter a number.", "danger")
            return redirect(url_for('play_game', level=level))

        # Decrease the number of attempts
        session['attempts'] -= 1

        if guess == correct_number:
            # User wins the game
            user.score += 10  # Add score for winning
            db.session.commit()
            session['game_status'] = 'win'  # Set game status to win
            flash(f"🎉 Correct! You guessed the number in {5 - session['attempts']} attempts.", "success")
            # Reset session after win
            session.pop('random_number', None)
            session.pop('attempts', None)
        elif session['attempts'] == 0:
            # Game over: User lost
            session['game_status'] = 'loss'  # Set game status to loss
            flash(f"Game Over! The correct number was {correct_number}.", "danger")
            # Reset session after loss
            session.pop('random_number', None)
            session.pop('attempts', None)
        elif guess < correct_number:
            flash("⬆ Too low! Try again.", "info")
        else:
            flash("⬇ Too high! Try again.", "info")

    session['game_status'] = 'pending'  # or 'win' / 'loss' after each guess

    return render_template('game.html', 
                           level=level, 
                           attempts=session.get('attempts', 5), 
                           score=user.score, 
                           username=user.username,
                           leaderboard=leaderboard_dicts, 
                           correct_number=correct_number,
                           game_status=game_status)

# Leaderboard
@app.route('/leaderboard')
def leaderboard():
    leaderboard_data = User.query.order_by(User.score.desc()).all()
    leaderboard = [{"username": user.username, "score": user.score} for user in leaderboard_data]
    return render_template('leaderboard.html', leaderboard=leaderboard)

@app.route('/reset')
def reset_game():
    session.pop('random_number', None)
    session.pop('attempts', None)
    level = session.get('level', 'easy')  # fallback level
    return redirect(url_for('play_game', level=level))

# Logout Route
@app.route('/logout')
@login_required
def logout():
    session.clear()
    flash("You have been logged out successfully.", "info")
    return redirect(url_for('home'))

# Run the application
if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # Create all tables
    app.run(debug=True)
