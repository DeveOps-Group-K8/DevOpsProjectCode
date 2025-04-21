import unittest
from flask import Flask, session
from app import app, db, User  # adjust based on your app structure

class NumberGuessingGameTestCase(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['LOGIN_DISABLED'] = False  # important for Flask-Login
        with app.app_context():
            db.create_all()
            test_user = User(username='testuser')
            test_user.set_password('testpass')
            db.session.add(test_user)
            db.session.commit()
        

    def login_session(client, number=7):
        with client:
            existing_user = User.query.filter_by(username='testuser').first()
            if existing_user:
                db.session.delete(existing_user)
                db.session.commit()

            password = 'password'
            hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
            user = User(username='testuser', password_hash=hashed_password, score=0, attempts=5)
            db.session.add(user)
            db.session.commit()

            client.post('/login', data=dict(username='testuser', password=password), follow_redirects=True)

            with client.session_transaction() as sess:
                sess['number_to_guess'] = number

 
    def test_correct_guess(self):
        self.login_session(self.app, number=7)
        response = self.app.post('/guess', data={'guess': '7'})
        self.assertEqual(response.status_code, 200)
