"""Message View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_message_views.py


import os
from unittest import TestCase

from models import db, connect_db, Message, User

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app, CURR_USER_KEY

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False


class MessageViewTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()

        self.client = app.test_client()

        self.test_user = User.signup(username="test",
                                    email="test@test.com",
                                    password="test",
                                    image_url=None)
        self.test_user.id = 666

        db.session.commit()

    def tearDown(self):
        resp = super().tearDown()
        db.session.rollback()
        return resp

    def test_authenticated_add_message(self):
        """Can an authenticated user add a message?"""

        # Since we need to change the session to mimic logging in,
        # we need to use the changing-session trick:

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.test_user.id

            # Now, that session setting is saved, so we can have
            # the rest of ours test

            resp = c.post("/messages/new", data={"text": "test"})

            # Make sure it redirects
            self.assertEqual(resp.status_code, 302)

            msg = Message.query.one()
            self.assertEqual(msg.text, "test")

    
    def test_unauthenticated_add_message(self):
        """Tests that an unauthenticated cannot create a new warble"""

        # user not logged in
        with self.client as c:
            resp = c.post("/messages/new", data={"text": "test"}, follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn('Access unauthorized.', str(resp.data))

        # invalid user (user does not exist)
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = 123456789

            resp = c.post("/messages/new", data={"text": "test"}, follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn('Access unauthorized.', str(resp.data))


    def test_authenticated_user_message_show(self):
        """Tests that an authenticated user can view messages"""

        # create test message attached to self.test_user
        message1 = Message(id=666, text='test', user_id=self.test_user.id)
        db.session.add(message1)
        db.session.commit()

        # test that test_user can view test message when logged into session
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.test_user.id

            message1 = Message.query.get(666)

            resp = c.get(f'/messages/{message1.id}')
            self.assertEqual(resp.status_code, 200)
            self.assertIn(message1.text, str(resp.data))

    def test_invalid_message_show(self):
        """Tests the 404 response for displaying (to an authenticated user) a message that doesn't exist"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.test_user.id

            resp = c.get('/messages/123456789')

            self.assertEqual(resp.status_code, 404)

    def test_unauthenticated_user_message_delete(self):
        """Tests that an unauthenticated user cannot delete messages"""
        
        # create test message for deletion, message tied to self.test_user
        message1 = Message(id=666, text='test', user_id=self.test_user.id)
        db.session.add(message1)
        db.session.commit()

        # tests that unauthenticated user cannot delete test message
        with self.client as c:
            message1 = Message.query.get(666)

            resp = c.post(f'/messages/{message1.id}/delete', follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn('Access unauthorized.', str(resp.data))
            self.assertIsNotNone(message1)

    def test_authenticated_user_message_delete(self):
        """Tests that an authenticated user can delete own messages"""      

        # create test message for deletion, message tied to self.test_user
        message1 = Message(id=666, text='test', user_id=self.test_user.id)
        db.session.add(message1)
        db.session.commit()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.test_user.id

            message1 = Message.query.get(666)

            resp = c.post(f'messages/{message1.id}/delete', follow_redirects=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Successfully deleted your warble.', str(resp.data))

            message1 = Message.query.get(666)
            self.assertIsNone(message1)