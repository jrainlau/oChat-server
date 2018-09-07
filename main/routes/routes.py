from .. import app, socketio, mongo
from flask import jsonify, request

@app.route('/')
def index():
    return jsonify({
        'message': 'Hello, World!'
    })

@app.route('/datas/add', methods = ['POST'])
def addUser():
    username = request.args['username']
    return 'xxx'


@app.route('/datas/find/<username>')
def getDatas(username):
    users = mongo.db.users
    user = users.find_one({'username': username})
    if (user):
        return str(user)
    else:
        return 'User ' + username + ' not found!'
