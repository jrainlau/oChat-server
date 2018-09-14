from ..controllers import UserController, ChatController, Manager
from .. import api

api.add_resource(UserController.UserRegistration, '/registration')
api.add_resource(UserController.UserLogin, '/login')
api.add_resource(UserController.UserLogoutAccess, '/logout/access')
api.add_resource(UserController.UserLogoutRefresh, '/logout/refresh')
api.add_resource(UserController.TokenRefresh, '/token/refresh')
api.add_resource(UserController.AllUsers, '/allUsers')
api.add_resource(UserController.UserExist, '/getUser')
api.add_resource(UserController.GetUserInfo, '/getUserInfo')
api.add_resource(UserController.EditProfile, '/editProfile')
api.add_resource(Manager.GenerateInviteCode, '/generateInviteCode')