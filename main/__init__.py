from flask import Flask
from flask_restful import Api
from flask_jwt_extended import JWTManager

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'secret!'
app.config['PROPAGATE_EXCEPTIONS'] = True
app.config['JWT_BLACKLIST_ENABLED'] = True
app.config['JWT_BLACKLIST_TOKEN_CHECKS'] = ['access', 'refresh']

blacklist = set()

api = Api(app)
jwt = JWTManager(app)

@jwt.token_in_blacklist_loader
def check_if_token_in_blacklist(decrypted_token):
    jti = decrypted_token['jti']
    return jti in blacklist

from .routes import routes
from .controllers import UserRegistration

api.add_resource(UserRegistration.UserRegistration, '/registration')
api.add_resource(UserRegistration.UserLogin, '/login')
api.add_resource(UserRegistration.UserLogoutAccess, '/logout/access')
api.add_resource(UserRegistration.UserLogoutRefresh, '/logout/refresh')
api.add_resource(UserRegistration.TokenRefresh, '/token/refresh')
api.add_resource(UserRegistration.AllUsers, '/allUsers')