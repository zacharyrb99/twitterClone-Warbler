import os
from unittest import TestCase
from models import db, User

os.environ['DATABASE_URL'] = 'postgresql:///warbler-test'

from app import app

db.create_all()

class UserModelTestCase(TestCase):
    def setUp(self):
        db.drop_all()
        db.create_all()

    def test_user_model(self):
        new_user = User(email='test@gmail.com', username='testuser', password='password')
        db.session.add(new_user)
        db.session.commit()

        test_user = User.query.get(1)

        self.assertEqual(test_user.email, 'test@gmail.com')
        self.assertEqual(test_user.username, 'testuser') 
        self.assertEqual(len(new_user.messages), 0)
        self.assertEqual(len(new_user.followers), 0)

    def test_user_follows(self):
        user1 = User(email='test1@gmail.com', username='test_user1', password='password')
        user2 = User(email='test2@gmail.com', username='test_user2', password='password')
        db.session.add_all([user1,user2])
        db.session.commit()
        
        user1.following.append(user2)
        db.session.commit()

        self.assertEqual(len(user2.followers), 1)
        self.assertEqual(len(user1.following), 1)

        self.assertEqual(user2.followers[0], user1)

    def test_is_following_and_is_followed(self):
        user1 = User(email='test1@gmail.com', username='test_user1', password='password')
        user2 = User(email='test2@gmail.com', username='test_user2', password='password')
        db.session.add_all([user1, user2])
        db.session.commit()

        user1.following.append(user2)
        db.session.commit()

        self.assertTrue(user1.is_following(user2))
        self.assertTrue(user2.is_followed_by(user1))