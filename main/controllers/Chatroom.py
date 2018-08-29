import functools
from .. import socketio
from flask_socketio import send, emit, disconnect, join_room, leave_room
from flask import request
from flask_jwt_extended import get_jti, decode_token

def message(msg, code):
    return {
        'message': msg,
        'code': code
    }

def authenticated_only(f):
    @functools.wraps(f)
    def wrapped(*args, **kwargs):
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
    emit('status', message({
        'status': 'joined',
        'user': user,
        'room': room
    }, 200), room = room)

@socketio.on('leave', namespace = '/chat')
@authenticated_only
def handleLeave(data):
    user = decode_token(request.args.get('token'))['identity']
    room = data['room']
    leave_room(room)
    emit('status', message({
        'status': 'left',
        'user': user,
        'room': room
    }, 200), room = room)

@socketio.on('text', namespace = '/chat')
@authenticated_only
def handleText(data):
    user = decode_token(request.args.get('token'))['identity']
    room = data['room']
    emit('message', message(user + ': ' + data['message'], 200), room = room)
