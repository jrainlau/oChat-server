from ..controllers import UserRegistration, Chatroom, Manager
from .. import api

api.add_resource(UserRegistration.UserRegistration, '/registration')
api.add_resource(UserRegistration.UserLogin, '/login')
api.add_resource(UserRegistration.UserLogoutAccess, '/logout/access')
api.add_resource(UserRegistration.UserLogoutRefresh, '/logout/refresh')
api.add_resource(UserRegistration.TokenRefresh, '/token/refresh')
api.add_resource(UserRegistration.AllUsers, '/allUsers')
api.add_resource(UserRegistration.UserExist, '/getUser')
api.add_resource(UserRegistration.EditProfile, '/editProfile')
api.add_resource(Manager.GenerateInviteCode, '/generateInviteCode')