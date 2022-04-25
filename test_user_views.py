"""Message View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_message_views.py


import os
from unittest import TestCase

from models import db, connect_db, Message, User, Likes

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


class UserViewTestCase(TestCase):
    """Test views for user."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()

        self.client = app.test_client()

        #create test users
        self.test_user1 = User.signup(username='test1',
                                    email='test@test.com',
                                    password='test',
                                    image_url=None)
        self.test_user1.id = 666

        self.test_user2 = User.signup(username='test2',
                                    email='test2@test.com',
                                    password='test',
                                    image_url=None)
        self.test_user2.id = 999

        self.test_user1.following.append(self.test_user2)

        db.session.commit()

        # add test messages for test_user1; have test_user2 like the test message
        warble = Message(id=666, text='testtesttest', user_id=self.test_user1.id)
        db.session.add(warble)
        db.session.commit()

        self.test_user2.likes.append(warble)
        db.session.commit()
        
    def tearDown(self):
        resp = super().tearDown()
        db.session.rollback()
        return resp

    
    def test_list_users(self):
        """Tests the search functionality for users"""

        with self.client as c:
            resp = c.get('/users')
            self.assertIn('@test1', str(resp.data))
            self.assertIn('@test2', str(resp.data))

    
    def test_users_show(self):
        """Tests whether the route displays a user in db"""

        with self.client as c:
            resp = c.get(f'/users/{self.test_user1.id}')
            self.assertIs(resp.status_code, 200)
            self.assertIn('@test1', str(resp.data))

    def test_show_following(self):
        """Tests whether the route displays the users the current user is following"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.test_user1.id

            resp = c.get(f'/users/{self.test_user1.id}/following')
            self.assertIs(resp.status_code, 200)
            self.assertIn('@test2', str(resp.data))


    def test_users_followers(self):
        """Tests whether the route displays the users who are following the current user"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.test_user2.id

            resp = c.get(f'/users/{self.test_user2.id}/followers')
            self.assertIs(resp.status_code, 200)
            self.assertIn('@test1', str(resp.data))

    
    def test_add_follow_invalid(self):
        """Tests that an unauthenticated user cannot follow another user"""
        with self.client as c:
            resp = c.post('users/follow/666', follow_redirects=True)
            self.assertIs(resp.status_code, 200)
            self.assertIn('Access unauthorized.', str(resp.data))


    def test_add_follow(self):
        """Tests whether an authenticated user can follow another user"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.test_user2.id

            resp = c.post('users/follow/666', follow_redirects=True)
            self.assertIs(resp.status_code, 200)
            self.assertIn('@test1', str(resp.data))


    def test_stop_following_invalid(self):
        """Tests whether an authenticated user can unfollow another user."""
        with self.client as c:
            resp = c.post('/users/stop-following/999', follow_redirects=True)
            self.assertIs(resp.status_code, 200)
            self.assertIn('Access unauthorized.', str(resp.data))


    def test_stop_following(self):
        """Tests whether an authenticated user can unfollow another user."""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.test_user1.id
            
            resp = c.post('/users/stop-following/999', follow_redirects=True)
            self.assertIs(resp.status_code, 200)
            self.assertIn('Stopped following test2', str(resp.data))


    def test_show_likes(self):
        """Tests whether the route displays the users likes"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.test_user2.id

            resp = c.get(f'/users/{self.test_user2.id}/likes')
            self.assertIs(resp.status_code, 200)
            self.assertIn('testtesttest', str(resp.data))

    def test_like_and_unlike(self):
        """Tests whether the like_message() view function allows user to like and unlike a message"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.test_user2.id

            # test that test_user2 can unlike a liked message
            resp=c.post('/users/add_like/666', follow_redirects=True)
            self.assertIs(resp.status_code, 200)

            likes = Likes.query.filter(Likes.message_id==666).all()
            self.assertEqual(len(likes), 0)

            # test that test_user2 can like an unliked message
            resp=c.post('/users/add_like/666', follow_redirects=True)
            self.assertIs(resp.status_code, 200)

            likes = Likes.query.filter(Likes.message_id==666).all()
            self.assertEqual(len(likes), 1)


    def test_unauthorized_like(self):
        """Test that unauthorized user cannot like messages"""
        with self.client as c:

            resp=c.post('/users/add_like/666', follow_redirects=True)
            self.assertIs(resp.status_code, 200)
            self.assertIn('Access unauthorized.', str(resp.data))





