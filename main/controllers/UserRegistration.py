from flask_restful import Resource, reqparse
from ..models.user import UserModel
from flask_jwt_extended import (create_access_token, create_refresh_token, jwt_required, jwt_refresh_token_required, get_jwt_identity, get_raw_jwt)
from .. import blacklist

parser = reqparse.RequestParser()
parser.add_argument('username', help = 'This field cannot be blank', required = True)
parser.add_argument('password', help = 'This field cannot be blank', required = True)

class UserRegistration(Resource):
    def post(self):
        parser_register = parser.copy()
        parser_register.add_argument('nickname', help = 'This field cannot be blank', required = True)
        parser_register.add_argument('inviteCode', help = 'This field cannot be blank', required = True)
        data = parser_register.parse_args()

        result = UserModel(data['username'], data['password'], data['nickname'], data['inviteCode']).registration()

        if isinstance(result, dict):
            access_token = create_access_token(identity = data['username'])
            refresh_token = create_refresh_token(identity = data['username'])
            result['access_token'] = access_token
            result['refresh_token'] = refresh_token
            return result
        else:
            return { 'message': result }, 500

class UserLogin(Resource):
    def post(self):
        data = parser.parse_args()
        user = UserModel(data['username'], data['password']).getUser()
        
        if user:
            access_token = create_access_token(identity = data['username'])
            refresh_token = create_refresh_token(identity = data['username'])
            user['access_token'] = access_token
            user['refresh_token'] = refresh_token
            return user
        else:
            return { 'message': 'Username is not exist or password incorrect!' }, 500

class UserLogoutAccess(Resource):
    @jwt_required
    def post(self):
        jti = get_raw_jwt()['jti']
        blacklist.add(jti)
        return { 'message': 'Successfully logged out' }, 200

class UserLogoutRefresh(Resource):
    @jwt_required
    def post(self):
        jti = get_raw_jwt()['jti']
        blacklist.add(jti)
        return { 'message': 'Successfully logged out' }, 200

class TokenRefresh(Resource):
    @jwt_refresh_token_required
    def post(self):
        current_user = get_jwt_identity()
        access_token = create_access_token(identity = current_user)
        return { 'access_token': access_token }

class AllUsers(Resource):
    @jwt_required
    def get(self):
        return UserModel.getAllUsers(self)