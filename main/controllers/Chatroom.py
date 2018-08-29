import functools
from .. import socketio
from flask_socketio import send, emit, disconnect, join_room, leave_room
from flask import request
from flask_jwt_extended import get_jti, decode_token

roomMap = dict()
userMap = dict()

def message(msg, code):
    return {
        'message': msg,
        'code': code
    }

def authenticated_only(f):
    @functools.wraps(f)
    def wrapped(*args, **kwargs):
        # get_jti(request.args.get('token'))
        # return f(*args, **kwargs)
        try:
            get_jti(request.args.get('token'))
            return f(*args, **kwargs)
        except BaseException as e:
            emit('Connect failed', message(str(e), 401))
    return wrapped

@socketio.on('connect', namespace = '/chat')
@authenticated_only
def handleConnect():
    emit('Connect successed', message('Connect successed!', 200))

@socketio.on('join', namespace = '/chat')
@authenticated_only
def handleJoin(data):
    user = decode_token(request.args.get('token'))['identity']
    room = data['room']
    join_room(room)
    if not room in roomMap:
        roomMap[room] = {
            'members': set()
        }
    roomMap[room]['members'].add(user)

    if not user in userMap:
        userMap[user] = {
            'joined_rooms': set()
        }
    userMap[user]['joined_rooms'].add(room)

    emit('status', message({
        'status': 'joined',
        'user': user,
        'current_room': room,
        'joined_rooms': [room for room in userMap[user]['joined_rooms']],
        'members': [member for member in roomMap[room]['members']]
    }, 200), room = room)

@socketio.on('leave', namespace = '/chat')
@authenticated_only
def handleLeave(data):
    user = decode_token(request.args.get('token'))['identity']
    room = data['room']
    leave_room(room)
    roomMap[room]['members'].remove(user)
    userMap[user]['joined_rooms'].remove(room)
    emit('status', message({
        'status': 'left',
        'user': user,
        'current_room': room,
        'joined_rooms': [room for room in userMap[user]['joined_rooms']],
        'members': [member for member in roomMap[room]['members']]
    }, 200), room = room)

@socketio.on('text', namespace = '/chat')
@authenticated_only
def handleText(data):
    user = decode_token(request.args.get('token'))['identity']
    room = data['room']
    emit('message', message({
        'user': user,
        'text': data['message']
    }, 200), room = room)
