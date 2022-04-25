"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase
from sqlalchemy import exc
from models import db, User, Message, Follows

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


class UserModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        # add two test users to test db
        test1 = User.signup(username= 'test1', password='test1', email='test1@test.com', image_url='https://images.unsplash.com/photo-1606326608606-aa0b62935f2b?ixlib=rb-1.2.1&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=1170&q=80')
        id1 = 666
        test1.id = id1

        test2 = User.signup(username= 'test2', password='test2', email='test2@test.com', image_url='https://images.unsplash.com/photo-1606326608606-aa0b62935f2b?ixlib=rb-1.2.1&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=1170&q=80')
        id2 = 999
        test2.id = id2

        db.session.commit()

        # save test users as self variables to access later
        test1 = User.query.get(id1)
        test2 = User.query.get(id2)

        self.test1 = test1
        self.test2 = test2

        self.id1 = id1
        self.id2 = id2

        self.client = app.test_client()

    def tearDown(self):
        """Tear down test client to start clean after each test"""
        # I had to look this part up in the solution; I am not too sure what super().tearDown() does?
        res = super().tearDown()
        db.session.rollback()
        return res


    def test_user_model(self):
        """Does basic model work?"""

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD",
        )

        db.session.add(u)
        db.session.commit()

        # User should have no messages & no followers
        self.assertEqual(len(u.messages), 0)
        self.assertEqual(len(u.followers), 0)


    def test_user_repr(self):
        """Does the repr method word as expected?"""

        res = self.test1.__repr__()
        self.assertEqual(res, "<User #666: test1, test1@test.com>")


    def test_user_follows(self):
        """Test whether test1 can follow test2, and test2 will have test1 listed as a follower"""
        self.test1.following.append(self.test2)
        db.session.commit()

        self.assertEqual(len(self.test1.following), 1)
        self.assertEqual(len(self.test2.followers), 1)


    def test_is_following(self):
        """Does is_following successfully detect when test1 is following test2?
        Does is_following successfully detect when test2 is not following test1?""" 

        self.test1.following.append(self.test2)
        db.session.commit()

        self.assertEqual(self.test1.is_following(self.test2), 1)
        self.assertEqual(self.test2.is_following(self.test1), 0)

    
    def test_is_followed_by(self):
        """Does is_followed_by successfully detect when test2 is followed by test1?
        Does is_followed_by successfully detect when test1 is not followed by test2?"""

        self.test1.following.append(self.test2)
        db.session.commit()

        self.assertEqual(self.test2.is_followed_by(self.test1), 1)
        self.assertEqual(self.test1.is_followed_by(self.test2), 0)

    
    def test_invalid_signup(self):
        """Tests that the validations on the User field run properly on username, email, and password"""

        # invalid username test
        user = User.signup(None, 'test@test.com', 'password', None)

        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()

        db.session.rollback()

        # invalid email test
        user = User.signup('test', None, "password", None)

        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()

        db.session.rollback()

        # invalid password test
        with self.assertRaises(ValueError) as context:
            User.signup('test', 'test@test.com', None, None)

    
    def test_user_authentication(self):
        """Does User.authenticate successfully return a user when given a valid username and password?
        Does User.authenticate fail to return a user when the username is invalid?
        Does User.authenticate fail to return a user when the password is invalid?"""

        test1 = User.authenticate('test1', 'test1')
        # test valid authentication
        self.assertEqual(self.test1.authenticate('test1', 'test1'), test1)

        # test invalid username
        self.assertEqual(self.test1.authenticate('wasedfj', 'test1'), False)

        #test invalid password
        self.assertEqual(self.test1.authenticate('test1', 'quwaygeuh'), False)