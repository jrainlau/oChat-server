import functools
from .. import socketio
from flask_socketio import send, emit, disconnect, join_room, leave_room
from flask import request
from flask_jwt_extended import get_jti, decode_token

def authenticated_only(f):
    @functools.wraps(f)
    def wrapped(*args, **kwargs):
        try:
            get_jti(request.args.get('token'))
            return f(*args, **kwargs)
        except BaseException as e:
            emit('Connect failed', {
                'message': str(e),
                'code': 401
            })
    return wrapped

@socketio.on('connect', namespace = '/chat')
@authenticated_only
def handleConnect():
    emit('Connect successed', 'Connect successed!')

@socketio.on('join', namespace = '/chat')
@authenticated_only
def handleJoin(data):
    tokenInfo = decode_token(request.args.get('token'))
    emit('join', tokenInfo)
