import ast
from passlib.hash import pbkdf2_sha256 as sha256
from .. import mongo

users = mongo.db.users
inviteCodes = mongo.db.inviteCodes

class UserModel():
    inviteCode = ''
    def __init__(self, username = '', password = '', inviteCode = '', avatar = ''):
        self.username = username
        self.password = password
        self.avatar = avatar
        UserModel.inviteCode = inviteCode

    @staticmethod
    def generate_hash(password):
        return sha256.hash(password)

    @staticmethod
    def verify_hash(password, hash):
        return sha256.verify(password, hash)

    def detail(self):
        return self.__dict__

    def getUser(self, noPsw = False):
        user = users.find_one({ 'username': self.username }, { '_id': False })
        if user:
            return user
        else:
            return {}

    def getAllUsers(self):
        allUsers = users.find({}, { '_id': False })
        return [user for user in allUsers]
            
    def isInvited(self):
        isInvited = False
        codesList = inviteCodes.find_one({})['list']
        objId = inviteCodes.find_one({})['_id']
        for code in codesList:
            if UserModel.inviteCode == str(code):
                isInvited = True
                codesList.remove(code)
                inviteCodes.update({ '_id': objId }, { '$set': {'list': codesList} })
                break
        return isInvited


    def registration(self):
        if not self.getUser() and self.isInvited():
            newUser = self.detail()
            newUser['password'] = UserModel.generate_hash(newUser['password'])
            users.insert(newUser)
            del newUser['password']
            del newUser['_id']
            return newUser
        elif self.getUser():
            return 'User was exist!'
        elif not self.isInvited():
            return 'Invite code error!'

    def editProfile(self):
        user = users.find_one({ 'username': self.username })
        if user:
            userId = user['_id']
            users.update({ '_id': userId }, {
                '$set': {
                    'username': self.username,
                    'avatar': self.avatar,
                    'password': self.password
                }
            })
            return {
                'username': self.username,
                'avatar': self.avatar,
            }
        else:
            return 'Username: ' + self.username + ' was not found!'


