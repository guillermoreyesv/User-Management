from flask import Flask
from application.routes import index
from application.views import users
from dotenv import load_dotenv
from flask_jwt_extended import JWTManager
import logging
import os


app = Flask(__name__)
load_dotenv()
app.config['JWT_SECRET_KEY'] = os.getenv('SECRET_KEY')
jwt = JWTManager(app)

level = logging.DEBUG if os.getenv('APP_MODE') == 'debug' else logging.WARNING
app.logger.setLevel(level)

app.add_url_rule(
    "/",
    view_func=index.Index.as_view("index")
    )

# Register and check profile user
app.add_url_rule(
    rule='/users',
    methods=['GET', 'POST'],
    view_func=users.ManageUser.as_view('users')
)

# Login
app.add_url_rule(
    rule='/users/login',
    methods=['POST'],
    view_func=users.Login.as_view('usersLogin')
)
