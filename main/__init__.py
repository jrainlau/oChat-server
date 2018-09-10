from flask import Flask
from flask_restful import Api
from flask_jwt_extended import JWTManager
from flask_socketio import SocketIO
from flask_cors import CORS
from flask_pymongo import PyMongo
import ast

dbauth = {}
with open('./datas/dbauth.txt') as f:
    dbauth = ast.literal_eval(f.read())

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'secret!'
app.config['PROPAGATE_EXCEPTIONS'] = True
app.config['JWT_BLACKLIST_ENABLED'] = True
app.config['JWT_BLACKLIST_TOKEN_CHECKS'] = ['access', 'refresh']
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = False
app.config['MONGO_URI'] = 'mongodb://' + dbauth['user'] + ':' + dbauth['pwd'] + '@0.0.0.0:27017/ochat'

blacklist = set()

api = Api(app)
jwt = JWTManager(app)
socketio = SocketIO(app, async_handlers=True)
mongo = PyMongo(app)
CORS(app, resources={r"/*":{"origins":"*"}}, supports_credentials=True)

@jwt.token_in_blacklist_loader
def check_if_token_in_blacklist(decrypted_token):
    jti = decrypted_token['jti']
    return jti in blacklist

from .routes import routes
