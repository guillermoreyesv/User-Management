from flask.views import MethodView
from flask import request


class ManageUser(MethodView):
    # Check Profile
    def get(self):
        from application import app
        from application.utils.user import User

        # Get Bearer Token
        authorization = request.headers.get('Authorization')

        # Validate Token
        info_user, user_collection = User.validate_token(authorization)
        if info_user is None:
            response = {
                'code': 401,
                'status': 'error',
                'message': 'Not a valid token.'
            }
            return response, response['code']

        # Preparing profile
        age = User.get_age(info_user['birthday'])
        response = {
            'id': str(info_user.get('_id')),
            'name': info_user.get('name'),
            'age': age,
            'token': info_user.get('access_token'),
            'comics_layaway': info_user.get('comics_layaway')
        }
        app.logger.debug(f'Profile response {response}')
        return response, 200

    # Register User
    def post(self):
        from application.utils.user import User
        from application.config.db import mongo
        from application.utils.request import Request
        from application import app

        # Params Dict
        status, params_received = Request.get_json(request)
        if not status:
            return params_received, params_received['code']

        # Check information
        response_validation = User.custom_validations(params_received)

        # If the information is not valid
        if response_validation['code'] != 200:
            return response_validation, response_validation['code']

        # Sanitize string
        email = params_received['email'].strip().lower()
        password = params_received['password'].strip()
        name = params_received['name'].strip()
        birthday = params_received['birthday']

        # Hash password
        hashed_password = User.hash_password(password=password)

        # Generate document
        user_dict = {
            'email': email,
            'password': hashed_password,
            'name': name,
            'birthday': User.transform_date(birthday)
        }

        # Get users collection
        try:
            user_collection = mongo.db.users
        except Exception as e:
            app.logger.error(f'Cant get user collection {e}')
            response = {
                'code': 500,
                'status': 'error',
                'message': 'Server error.'
            }
            return response, response['code']

        # Check if user is already register
        results = user_collection.find_one({'email': email})
        if results:
            user_dict.pop('password')
            response = {
                'code': 409,
                'status': 'failed',
                'message': 'User is already registered',
                'params': user_dict
            }
            app.logger.warning(f'User is already registered {response}')
            return response, response['code']

        # Save document
        result = user_collection.insert_one(user_dict)

        # Remove sensible information
        user_dict.pop('password')
        user_dict.pop('_id')

        # If document was saved
        if result.acknowledged:
            response = {
                'code': 200,
                'status': 'ok',
                'message': 'User has been registered',
                'params': user_dict
            }
            app.logger.debug(f'User has been registered {response}')
        else:
            response = {
                'code': 500,
                'status': 'failed',
                'message': 'User has not been registered',
                'params': user_dict
            }

        # Response
        return response, response['code']


class Login(MethodView):
    def post(self):
        from application.utils.user import User
        from application.config.db import mongo
        from application.utils.request import Request
        from flask_jwt_extended import create_access_token
        from application import app

        # Params Dict
        status, params_received = Request.get_json(request)
        if not status:
            return params_received, params_received['code']

        email = params_received.get('email', '').strip().lower()
        password = params_received.get('password', '').strip()

        # Check email and password length
        if len(email) == 0 or len(password) == 0:
            response = {
                'code': 400,
                'status': 'failed',
                'message': 'User or password empty.'
            }
            app.logger.warning(f'User or password empty params:{params_received} response:{response}')
            return response, response['code']

        # Hash password
        hashed_password = User.hash_password(password=password)

        # Get users collection
        try:
            user_collection = mongo.db.users
        except Exception as e:
            app.logger.error('Cant get user collection', e)
            response = {
                'code': 500,
                'status': 'error',
                'message': 'Server error.'
            }
            return response, response['code']

        # Find user document
        dict_to_find = {'email': email, 'password': hashed_password}
        user = user_collection.find_one(dict_to_find)

        # If not found document
        if not user:
            response = {
                'code': 404,
                'status': 'failed',
                'message': 'User not found or password incorrect.'
            }
            app.logger.warning(f'User not found params:{params_received} response:{response}')
            return response, response['code']

        # Create the access token
        access_token = create_access_token(identity=email)

        # Save token
        dict_to_match = {'_id': user['_id']}
        dict_to_update = {'$set': {'access_token': access_token}}
        result = user_collection.update_one(dict_to_match, dict_to_update)

        # Check result
        if result.acknowledged:
            response = {
                'token': access_token,
                'email': email,
                'code': 200,
                'message': 'ok'
            }
            app.logger.debug(f'Token saved {response}')

        else:
            response = {
                'code': 500,
                'email': email,
                'message': 'Server error'
            }
            app.logger.error(f'Token not saved {response}')
        return response, response['code']
