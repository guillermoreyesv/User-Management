class User():
    def check_email(email=''):
        import re
        response = {
            'status': False,
            'email': email
        }
        email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        if re.match(email_regex, email):
            response['status'] = True
        return response

    def hash_password(password=''):
        import hashlib

        hash_md5 = hashlib.md5()
        hash_md5.update(password.encode())

        return hash_md5.hexdigest()

    def transform_date(date=''):
        from datetime import datetime
        date = date.strip()
        datetime.strptime(date, '%Y-%m-%d')
        return date

    def custom_validations(params):
        from application import app
        # Clone dict values into a new one
        new_params = params.copy()
        # Remove password value in new dictionary
        if params.get('password'):
            new_params.pop('password')

        # Default response if any goes wrong
        response = {
            'code': 500,
            'status': 'error',
            'message': 'api error',
            'params': new_params
        }

        if not params.get('email'):
            response['message'] = 'Missing email.'
            response['status'] = 'error'
            response['code'] = 400
            return response

        if not params.get('password'):
            response['message'] = 'Missing password.'
            response['status'] = 'error'
            response['code'] = 400
            return response

        if not params.get('name'):
            response['message'] = 'Missing name.'
            response['status'] = 'error'
            response['code'] = 400
            return response

        if not params.get('birthday'):
            response['message'] = 'Missing birthday.'
            response['status'] = 'error'
            response['code'] = 400
            return response

        # Checking birthday date format
        birthday = params['birthday']
        try:
            User.transform_date(birthday)
        except Exception as e:
            app.logger.error(f'Birthday format mismatch {birthday} {e}')
            response['message'] = 'Birthday format mismatch. YYYY-MM-DD (ISO 8601)'
            response['status'] = 'error'
            response['code'] = 400
            return response

        # Checking email
        response_email = User.check_email(email=params['email'])
        if response_email['status'] is False:
            response['message'] = 'Email format mismatch.'
            response['status'] = 'error'
            response['code'] = 400
            return response

        # ALL OK
        response = {
            'code': 200,
            'status': 'ok',
            'message': 'valid information'
        }
        return response

    def get_age(date):
        from datetime import datetime
        birthday = datetime.strptime(date, '%Y-%m-%d')
        now = datetime.now()
        datetime_difference = now - birthday
        age = int(datetime_difference.days/365)
        return age

    def validate_token(token):
        from application.config.db import mongo
        from application import app

        results = None
        user_collection = None

        if not token:
            app.logger.error(f'token is {token}')
            return results, user_collection

        start_with_bearer = token.startswith('Bearer ')

        if not start_with_bearer:
            app.logger.error(f'token not start with Bearer {token}')
            return results, user_collection

        token = token[7:]

        # Get users collection
        try:
            user_collection = mongo.db.users
        except Exception as e:
            app.logger.error(f'Cant get user collection {e}')
            return results

        # Find user by token
        results = user_collection.find_one({'access_token': token})
        if not results:
            app.logger.error(f'User not found {token}')

        return results, user_collection
