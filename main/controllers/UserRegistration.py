from flask_restful import Resource, reqparse
# from ..models.user import UserModel
from ..models.UserModel import UserModel
from flask_jwt_extended import (create_access_token, create_refresh_token, jwt_required, jwt_refresh_token_required, get_jwt_identity, get_raw_jwt)
from .. import blacklist
from .Chatroom import roomMap
import werkzeug

parser = reqparse.RequestParser()
parser.add_argument('username', help = 'This field cannot be blank', required = True)
parser.add_argument('password', help = 'This field cannot be blank', required = True)

class UserRegistration(Resource):
    def post(self):
        parser_register = parser.copy()
        parser_register.add_argument('inviteCode', help = 'This field cannot be blank', required = True)
        parser_register.add_argument('avatar')
        data = parser_register.parse_args()

        result = UserModel(data['username'], data['password'], data['inviteCode'], data['avatar']).registration()

        if isinstance(result, dict):
            access_token = create_access_token(identity = data['username'])
            refresh_token = create_refresh_token(identity = data['username'])
            result['access_token'] = access_token
            result['refresh_token'] = refresh_token
            return { 'message': result }, 200
        else:
            return { 'message': result }, 500

class UserExist(Resource):
    def post(self):
        parser_exist = reqparse.RequestParser()
        parser_exist.add_argument('username', help = 'This field cannot be blank', required = True)
        data = parser_exist.parse_args()

        result = UserModel(data['username']).getUser(noPsw = True)
        return { 'message': result }, 200

class UserLogin(Resource):
    def post(self):
        data = parser.parse_args()
        user = UserModel(data['username'], data['password']).getUser()
        
        if 'username' in user:
            access_token = create_access_token(identity = data['username'])
            refresh_token = create_refresh_token(identity = data['username'])
            user['access_token'] = access_token
            user['refresh_token'] = refresh_token
            return { 'message': user }, 200
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
        return {
            'message': {
                'access_token': access_token
            }
        }, 200

class AllUsers(Resource):
    @jwt_required
    def get(self):
        return UserModel.getAllUsers(self)

class EditProfile(Resource):
    @jwt_required
    def post(self):
        parserProfile = parser.copy()
        parserProfile.add_argument('newAvatar')
        parserProfile.add_argument('newName')
        parserProfile.add_argument('newPassword')
        data = parserProfile.parse_args()

        result = UserModel(data['username'], data['password']).editProfile(data['newName'], data['newPassword'], data['newAvatar'])

        if isinstance(result, dict):
            return { 'message': result }, 200
        else:
            return { 'message': result }, 500
