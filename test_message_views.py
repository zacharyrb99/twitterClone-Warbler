import os
from unittest import TestCase
from models import db, Message, User

os.environ['DATABASE_URL'] = 'postgresql:///warbler-test'

from app import CURR_USER_KEY, app

db.create_all()
app.config['WTF_CSRF_ENABLED'] = False

class MessageViewTestCase(TestCase):
    def setUp(self):
        db.drop_all()
        db.create_all()
        
        self.test_user = User.signup(username='test_user', email='test@gmail.com', password='password', image_url=None)
        self.test_user_id = 999
        self.test_user.id = self.test_user_id

        db.session.commit()

    def test_add_message(self):
        with app.test_client() as client:
            with client.session_transaction() as session:
                session[CURR_USER_KEY] = self.test_user.id

            response = client.post('/messages/new', data={'text': 'First message'})

            self.assertEqual(response.status_code, 302)

            msg = Message.query.get(1)
            self.assertEqual(msg.text, 'First message')

    def test_add_unauthorized_msg(self):
        with app.test_client() as client:
            response = client.post('/messages/new', data={'text': 'First Message'}, follow_redirects=True)
            s = str(response.data)
            
            self.assertEqual(response.status_code, 200)
            self.assertIn("Access unauthorized", s)

    def test_show_messages(self):
        msg = Message(text='Test Message', user_id=self.test_user_id)
        db.session.add(msg)
        db.session.commit()

        with app.test_client() as client:
            with client.session_transaction() as session:
                session[CURR_USER_KEY] = self.test_user_id

            m = Message.query.get(1)
            response = client.get(f'/messages/{m.id}')
            s = str(response.data)

            self.assertEqual(response.status_code, 200)
            self.assertEqual(m.id, 1)
            self.assertIn('Test Message', s)

    def test_show_invalid_message(self):
        with app.test_client() as client:
            with client.session_transaction() as session:
                session[CURR_USER_KEY] = self.test_user_id

            response = client.get('/messages/43284238')

            self.assertEqual(response.status_code, 500)

    def test_delete_message(self):
        msg = Message( text='Test Message', user_id=self.test_user_id)
        db.session.add(msg)
        db.session.commit()

        with app.test_client() as client:
            with client.session_transaction() as session:
                session[CURR_USER_KEY] = self.test_user_id

            response = client.post('/messages/1/delete', follow_redirects=True)
            self.assertEqual(response.status_code, 200)

            m = Message.query.get(1)
            self.assertIsNone(m)

    

    