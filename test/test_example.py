import unittest
from app import app, db, User

from flask import session
from flask.testing import FlaskClient


class NumberGuessingGameTestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:9257postgres@localhost/users'
      
        self.app = app.test_client()
        self.ctx = app.app_context()
        self.ctx.push()
        db.create_all()

        # Create test user
        self.test_user = User(username="testuser")
        self.test_user.set_password("testpassword")

        db.session.add(self.test_user)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.ctx.pop()

    def login_session(self, client: FlaskClient, number=7):
        """Helper to simulate a session with a logged-in user and a number to guess."""
        with client.session_transaction() as sess:
            sess['user_id'] = self.test_user.id
            sess['number'] = number
            sess['attempts'] = 0
            sess['level'] = 'easy'  # Required for reset

    def test_correct_guess(self):
        with self.app as client:
            self.login_session(client, number=7)
            response = client.post('/guess', data={'guess': '7'})
            json_data = response.get_json()
            self.assertEqual(response.status_code, 200)
            self.assertEqual(json_data['result'], 'Correct! You guessed it!')

    def test_high_guess(self):
        with self.app as client:
            self.login_session(client, number=3)
            response = client.post('/guess', data={'guess': '10'})
            json_data = response.get_json()
            self.assertEqual(response.status_code, 200)
            self.assertEqual(json_data['result'], 'Too high!')

    def test_low_guess(self):
        with self.app as client:
            self.login_session(client, number=10)
            response = client.post('/guess', data={'guess': '5'})
            json_data = response.get_json()
            self.assertEqual(response.status_code, 200)
            self.assertEqual(json_data['result'], 'Too low!')

    def test_invalid_input(self):
        with self.app as client:
            self.login_session(client, number=5)
            response = client.post('/guess', data={'guess': 'abc'})
            self.assertEqual(response.status_code, 400)
            self.assertIn(b'Invalid input', response.data)

    def test_reset_game(self):
        with self.app as client:
            self.login_session(client)
            response = client.get('/reset')
            self.assertEqual(response.status_code, 302)  # Expect redirect


if __name__ == '__main__':
    unittest.main()
#     app.run(debug=True)