import os
from unittest import TestCase
from models import db, User, Message, Likes

os.environ['DATABASE_URL'] = 'postgresql:///warbler-test'

from app import app

db.create_all()

class MessageModelTestCase(TestCase):
    def setUp(self):
        db.drop_all()
        db.create_all()

        self.user_id = 999
        user = User.signup(username='test_user', email='test@gmail.com', password='password', image_url=None)
        user.id = self.user_id

        db.session.add(user)
        db.session.commit()

        self.user = User.query.get(self.user_id)

    def test_message(self):
        msg = Message(text='My first message', user_id=self.user_id)
        db.session.add(msg)
        db.session.commit()

        self.assertEqual(len(self.user.messages), 1)
        self.assertEqual(self.user.messages[0].text, 'My first message')