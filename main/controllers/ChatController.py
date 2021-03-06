import functools
import time

from flask_socketio import emit, disconnect, join_room, leave_room
from flask import request
from flask_jwt_extended import get_jti, decode_token

from ..utils.roomName import generateRoomName
from ..models.UserModel import UserModel
from .. import socketio

roomMap = dict()
userMap = dict()

def message(msg, code):
    if isinstance(msg, dict):
        msg['time'] = time.strftime("%Y-%m-%d %H:%M", time.localtime())
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

@socketio.on('connect', namespace = '/')
@authenticatedOnly
def handleConnect():
    user = decode_token(request.args.get('token'))['identity']
    joinedRooms = []
    if user in userMap:
        joinedRooms = userMap[user]['joinedRooms']

    emit('Connect successed', message({
        'status': 'connect',
        'joinedRooms': joinedRooms,
    }, 200))

@socketio.on('create', namespace = '/')
@authenticatedOnly
def handleCreate(data):
    user = decode_token(request.args.get('token'))['identity']
    room = data['roomId']
    avatar = UserModel(user).getUser(noPsw = True)['avatar']
    avatarMap = {
        'user': user,
        'avatar': avatar
    }
    if 'roomName' in data and data['roomName']:
        roomName = data['roomName']
    else:
        roomName = generateRoomName()

    join_room(room)

    roomMap[room] = {
        'members': [user],
        'roomId': room,
        'roomName': roomName,
        'avatarList': [avatarMap]
    }

    if not user in userMap:
        userMap[user] = {
            'joinedRooms': []
        }
    thisRoom = {
        'roomName': roomName,
        'roomId': room,
        'members': roomMap[room]['members']
    }
    
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

@socketio.on('join', namespace = '/')
@authenticatedOnly
def handleJoin(data):
    user = decode_token(request.args.get('token'))['identity']
    room = data['roomId']
    avatar = UserModel(user).getUser(noPsw = True)['avatar']
    avatarMap = {
        'user': user,
        'avatar': avatar
    }

    if not room in roomMap:
        emit('status', message({
            'status': 'join failed'
        }, 200))
        return False

    if not user in roomMap[room]['members']:
        roomMap[room]['members'].append(user)
        roomMap[room]['avatarList'].append(avatarMap)

    if not user in userMap:
        userMap[user] = {
            'joinedRooms': []
        }
    thisRoom = {
        'roomName': roomMap[room]['roomName'],
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
        'avatarList': roomMap[room]['avatarList'],
        'roomId': room,
        'roomName': roomMap[room]['roomName'],
        'joinedRooms': userMap[user]['joinedRooms'],
        'members': roomMap[room]['members']
    }, 200), room = room)

@socketio.on('leave', namespace = '/')
@authenticatedOnly
def handleLeave(data):
    user = decode_token(request.args.get('token'))['identity']
    room = data['roomId']

    def removeUser(member):
        return member != user

    def removeJoinedRoom(theRoom):
        return theRoom['roomId'] != room
    
    def removeAvatar(avatarMap):
        return avatarMap['user'] != user

    roomMap[room]['members'] = list(filter(removeUser, roomMap[room]['members']))
    userMap[user]['joinedRooms'] = list(filter(removeJoinedRoom, userMap[user]['joinedRooms']))
    roomMap[room]['avatarList'] = list(filter(removeAvatar, roomMap[room]['avatarList']))

    emit('status', message({
        'status': 'left',
        'user': user,
        'roomId': room,
        'roomName': roomMap[room]['roomName'],
        'joinedRooms': userMap[user]['joinedRooms'],
        'members': roomMap[room]['members']
    }, 200), room = room)

    leave_room(room)

@socketio.on('text', namespace = '/')
@authenticatedOnly
def handleText(data):
    user = decode_token(request.args.get('token'))['identity']
    room = data['roomId']
    emit('message', message({
        'user': user,
        'text': data['message'],
        'roomId': roomMap[room]['roomId'],
        'roomName': roomMap[room]['roomName']
    }, 200), room = room)

@socketio.on('rename', namespace = '/')
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

