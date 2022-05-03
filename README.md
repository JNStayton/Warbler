## Warbler (A Twitter Clone)

### Requirements and Dependencies:
This app uses PostgreSQL and connects to a database named 'warbler'. Be sure to create the database in psql:
```sql
CREATE DATABASE warbler
```

Run the following commands in the terminal:
1. `python3 -m venv venv` to create a virtual environment
2. `pip3 install -r requirements.txt` to install the current dependencies in the necessary versions
3. `source venv/bin/activate` to activate the virtual environment
4. `flask run` to start the flask server and run the program

If you would like to start the program with prepopulated data to play around with, please run the following command in ipython:
1. `%run seed.py` run the seed file to prepopulate the database with users, posts, and profile info


### Warbler
In a nutshell, the schema is many-to-many. One **User** may create many **Messages**, may follow many **Users**, may like many **Messages** by many **Users**.

An unlogged-in user is always redirected to the login/register page.
A logged-in user is directed to their own homepage, where their stats (messages/follows/followers) are displayed, as well as the most recent messages posted by users they have followed.

**A logged-in user may:**
1. Follow another user
2. Like another user's message
3. View their followers
4. View who they are following
5. Create a new message
6. View the messages they have created
7. View the messages they have liked
8. Unlike a message
9. Unfollow a user
10. View another user's profile
11. View their own profile
12. Edit their own profile
13. Delete their account

**A logged-in user may not:**
1. Alter or delete messages, likes, follows, followers, or profiles of another user
2. Like their own messages
3. Follow themselves


### Warbler Tests
To run the tests, make sure you create the 'warbler-test' PostgreSQL database with psql. 
```sql
CREATE DATABASE warbler-test
```

1. test_message_model.py 
>> This file contains tests for the Message model in models.py, inlcuding 'like' functionality.

2. test_message_views.py
>> This file contains tests for all the view funcs in app.py related to Messages, including authentication.

3. test_user_model.py
>> This file contains tests for the User model in models.py, including user registration, login, the relationship between User and Message, the functionality of Follows, and the functionality of Likes. 

4. test_user_views.py
>> This file contains tests for all the view funcs in app.py related to Users, including login verification and authentication, redirection, searching and displaying Users, and likes and follows functionality. 