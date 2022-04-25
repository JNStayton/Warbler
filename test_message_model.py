"""Message model tests."""

# run these tests like:
#
#    python -m unittest test_message_model.py


import os
from unittest import TestCase
from sqlalchemy import exc

from models import db, User, Message

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()


class MessageModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""
        db.drop_all()
        db.create_all()

        test1 = User.signup(username= 'test1', password='test1', email='test1@test.com', image_url='https://images.unsplash.com/photo-1606326608606-aa0b62935f2b?ixlib=rb-1.2.1&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=1170&q=80')
        id1 = 666
        test1.id = id1
        db.session.commit()

        self.test_user = User.query.get(666)

        self.client = app.test_client()

    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res

    def test_model(self):
        """Test that the basic message model works"""

        warble = Message(text='test', user_id=self.test_user.id)
        db.session.add(warble)
        db.session.commit()

        self.assertEqual(self.test_user.messages[0], warble)

    
    def test_message_likes(self):
        """Test that the likes relationship between User and Message works"""

        warble = Message(text='test', user_id=self.test_user.id)
        db.session.add(warble)
        db.session.commit()

        test_user2 = User.signup('test2', 'test2@test.com', 'test', None)
        test_user2.id = 999
        db.session.commit()

        warble2 = Message(text='test', user_id=test_user2.id)
        db.session.add(warble2)
        db.session.commit()

        test_user2.likes.append(warble)
        self.test_user.likes.append(warble2)
        db.session.commit()

        self.assertEqual(test_user2.likes[0], warble)
        self.assertEqual(self.test_user.likes[0], warble2)