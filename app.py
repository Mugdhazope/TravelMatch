from flask import Flask, render_template, request, redirect, flash, url_for, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your_secret_keyasdsada'  # Needed for flash messages and sessions
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///TravelMatch.db"
db = SQLAlchemy(app)

class User(db.Model):
    userId = db.Column(db.Integer, primary_key=True, autoincrement=True)
    userName = db.Column(db.String(200), unique=True, nullable=False)  # Ensure usernames are unique
    password = db.Column(db.String(200), nullable=False)
    realName = db.Column(db.String(200), nullable=False)

    def __repr__(self) -> str:
        return f"{self.userId} - {self.userName}"

class Ratings(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    userId = db.Column(db.Integer, nullable=False)
    postId = db.Column(db.Integer, nullable=False)
    rating = db.Column(db.Integer, nullable=False)

    def __repr__(self) -> str:
        return f"{self.userId} - {self.postId}"

class Posts(db.Model):
    postId = db.Column(db.Integer, primary_key=True, autoincrement=True)
    location = db.Column(db.String(200), nullable=False)
    userId = db.Column(db.Integer, nullable=False)
    caption = db.Column(db.String(200), nullable=False)

    def __repr__(self) -> str:
        return f"{self.userId} - {self.postId}"

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        realName = request.form['realname']

        # Check if the username already exists
        existing_user = User.query.filter_by(userName=username).first()
        if existing_user:
            flash('Username already exists! Please choose a different username.')
            return redirect(url_for('register'))

        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        newuser = User(userName=username, password=hashed_password, realName=realName)
        db.session.add(newuser)
        db.session.commit()
        flash('Registration successful! Please log in.')
        return redirect(url_for('login'))

    return render_template("index.html")

@app.route('/signin', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(userName=username).first()
        
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.userId  # Store user ID in session
            flash('Login successful!')
            return redirect(url_for('mainpage'))
        else:
            flash('Invalid username or password')

    return render_template('login.html')

@app.route('/mainpage', methods=['GET', 'POST'])
def mainpage():
    if 'user_id' not in session:
        flash('Please log in to access the main page.')
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    print(user)  # Get the current user
    return render_template('mainpage.html', user=user)

@app.route('/')
def firstPage():
    return render_template("first.html")

@app.route('/logout')
def logout():
    session.pop('user_id', None)  # Remove user ID from session
    flash('You have been logged out.')
    return redirect(url_for('firstPage'))

if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # Create the database tables
    app.run(debug=True)
