from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from flask_bcrypt import Bcrypt

# Initialize the database object only once
 
db = SQLAlchemy()
bcrypt = Bcrypt()
 
# Database Model for User
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    score = db.Column(db.Integer, default=0, nullable=False)
    attempts = db.Column(db.Integer, default=5, nullable=False) 

    def set_password(self, password):
        """Hash the password before storing it."""
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        """Verify the password during login."""
        return bcrypt.check_password_hash(self.password_hash, password)

    def to_dict(self):
        """Convert the User object to a dictionary."""
        return {
            'id': self.id,
            'username': self.username,
            'score': self.score
        }
