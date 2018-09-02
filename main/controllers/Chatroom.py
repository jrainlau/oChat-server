import functools
from .. import socketio
from flask_socketio import send, emit, disconnect, join_room, leave_room
from flask import request
from flask_jwt_extended import get_jti, decode_token
from ..utils.roomName import generateRoomName
from ..models.user import UserModel

roomMap = dict()
userMap = dict()

def message(msg, code):
    return {
        'message': msg,
        'code': code
    }

def authenticatedOnly(f):
    @functools.wraps(f)
    def wrapped(*args, **kwargs):
        try:
            get_jti(request.args.get('token'))
            return f(*args, **kwargs)
        except BaseException as e:
            emit('Connect failed', message(str(e), 401))
    return wrapped

@socketio.on('connect', namespace = '/chat')
@authenticatedOnly
def handleConnect():
    emit('Connect successed', message('Connect successed!', 200))

@socketio.on('create', namespace = '/chat')
@authenticatedOnly
def handleCreate(data):
    user = decode_token(request.args.get('token'))['identity']
    room = data['roomId']
    avatar = UserModel(user).getUser(noPsw = True)['avatar']
    if 'roomName' in data and data['roomName']:
        roomName = data['roomName']
    else:
        roomName = generateRoomName()

    join_room(room)

    roomMap[room] = {
        'members': [],
        'roomId': room,
        'roomName': roomName
    }

    if not user in roomMap[room]['members']:
        roomMap[room]['members'].append(user)

    if not user in userMap:
        userMap[user] = {
            'joinedRooms': []
        }
    thisRoom = {
        'roomName': roomName,
        'roomId': room,
        'members': roomMap[room]['members']
    }
    if not room in [room['roomId'] for room in userMap[user]['joinedRooms']]:
        userMap[user]['joinedRooms'].append(thisRoom)

    emit('status', message({
        'status': 'created',
        'user': user,
        'avatar': avatar,
        'roomId': room,
        'roomName': roomName,
        'joinedRooms': userMap[user]['joinedRooms'],
        'members': roomMap[room]['members']
    }, 200), room = room)

@socketio.on('join', namespace = '/chat')
@authenticatedOnly
def handleJoin(data):
    user = decode_token(request.args.get('token'))['identity']
    room = data['roomId']
    avatar = UserModel(user).getUser(noPsw = True)['avatar']

    if not room in roomMap:
        emit('status', message({
            'status': 'join failed'
        }))
        return False

    if not user in roomMap[room]['members']:
        roomMap[room]['members'].append(user)

    if not user in userMap:
        userMap[user] = {
            'joinedRooms': []
        }
    thisRoom = {
        'roomName': roomMap[room]['roomname'],
        'roomId': room,
        'members': roomMap[room]['members']
    }
    if not room in [room['roomId'] for room in userMap[user]['joinedRooms']]:
        userMap[user]['joinedRooms'].append(thisRoom)

    join_room(room)

    emit('status', message({
        'status': 'joined',
        'user': user,
        'avatar': avatar,
        'roomId': room,
        'roomName': roomName,
        'joinedRooms': userMap[user]['joinedRooms'],
        'members': roomMap[room]['members']
    }, 200), room = room)

@socketio.on('leave', namespace = '/chat')
@authenticatedOnly
def handleLeave(data):
    user = decode_token(request.args.get('token'))['identity']
    room = data['roomId']

    def removeUser(member):
        return member != user

    def removeJoinedRoom(theRoom):
        return theRoom['roomId'] != room

    roomMap[room]['members'] = list(filter(removeUser, roomMap[room]['members']))
    userMap[user]['joinedRooms'] = list(filter(removeJoinedRoom, userMap[user]['joinedRooms']))

    emit('status', message({
        'status': 'left',
        'user': user,
        'roomId': room,
        'roomName': roomMap[room]['roomName'],
        'joinedRooms': userMap[user]['joinedRooms'],
        'members': roomMap[room]['members']
    }, 200), room = room)

    leave_room(room)

@socketio.on('text', namespace = '/chat')
@authenticatedOnly
def handleText(data):
    user = decode_token(request.args.get('token'))['identity']
    room = data['roomId']
    emit('message', message({
        'user': user,
        'text': data['message']
    }, 200), room = room)

@socketio.on('rename', namespace = '/chat')
@authenticatedOnly
def handleChangeRoomName(data):
    user = decode_token(request.args.get('token'))['identity']
    room = data['roomId']
    newRoomName = data['newRoomName']
    roomMap[room]['roomName'] = newRoomName
    for theUser in userMap.items():
        for joinedRoom in theUser[1]['joinedRooms']:
            if joinedRoom['roomId'] == room:
                joinedRoom['roomName'] = newRoomName
    
    emit('status', message({
        'status': 'rename',
        'user': user,
        'roomId': room,
        'roomName': roomMap[room]['roomName'],
        'joinedRooms': userMap[user]['joinedRooms'],
        'members': roomMap[room]['members']
    }, 200), room = room)

