import os
from unittest import TestCase
from models import db, connect_db, Message, User, Likes, Follows

os.environ['DATABASE_URL'] = 'postgresql:///warbler-test'

from app import app, CURR_USER_KEY

db.create_all()
app.config['WTF_CSRF_ENABLED'] = False

class MessageViewTestCase(TestCase):
    def setUp(self):
        db.drop_all()
        db.create_all()

        self.test_user = User.signup(username='test_user', email='test@gmail.com', password='password', image_url=None)
        self.test_user_id = 999
        self.test_user.id = self.test_user_id

        self.user1 = User.signup(username='user1', email='user1@gmail.com', password='password', image_url=None)
        self.user1_id = 888
        self.user1.id = self.user1_id

        self.user2 = User.signup(username='user2', email='user2@gmail.com', password='password', image_url=None)
        self.user2_id = 777
        self.user2.id = self.user2_id
    
        db.session.add_all([self.test_user, self.user1, self.user2])
        db.session.commit()

    def test_users_page(self):
        with app.test_client() as client:
            response = client.get('/users')
            s = str(response.data)

            self.assertIn('@test_user', s)
            self.assertIn('@user1', s)
            self.assertIn('@user2', s)

    def test_users_search(self):
        with app.test_client() as client:
            response = client.get('/users?q=test')
            s = str(response.data)

            self.assertIn('@test_user', s)
            self.assertNotIn('@user1', s)

    def test_show_user(self):
        with app.test_client() as client:
            response = client.get(f'/users/{self.test_user_id}')
            s = str(response.data)

            self.assertEqual(response.status_code, 200)
            self.assertIn('@test_user', s)

    def test_like(self):
        msg = Message(id=999, text='Test Message', user_id=self.user1_id)
        db.session.add(msg)
        db.session.commit()

        with app.test_client() as client:
            with client.session_transaction() as session:
                session[CURR_USER_KEY] = self.test_user_id

            response = client.post('/messages/999/like', follow_redirects=True)
            self.assertEqual(response.status_code, 200)

            likes = Likes.query.filter(Likes.message_id==999).all()
            self.assertEqual(len(likes), 1)
            self.assertEqual(likes[0].user_id, self.test_user_id)

    def test_unlike(self):
        msg = Message(id=999, text='Test Message', user_id=self.user1_id)
        db.session.add(msg)
        db.session.commit()

        like = Likes(user_id=self.test_user_id, message_id=999)
        db.session.add(like)
        db.session.commit()

        m = Message.query.get(999)
        self.assertIsNotNone(m)

        l = Likes.query.get(1)
        self.assertIsNotNone(l)

        with app.test_client() as client:
            with client.session_transaction() as session:
                session[CURR_USER_KEY] = self.test_user_id

            response = client.post('/messages/999/like', follow_redirects=True)
            self.assertEqual(response.status_code, 200)

            likes = Likes.query.filter(Likes.message_id==999).all()
            self.assertEqual(len(likes), 0)
