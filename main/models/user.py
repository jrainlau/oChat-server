import ast
from passlib.hash import pbkdf2_sha256 as sha256

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
        user = {}
        with open('./datas/userList.txt') as f:
            for line in f.readlines():
                existUser = ast.literal_eval(line)
                if not noPsw:
                    if self.username == existUser['username'] and UserModel.verify_hash(self.password, existUser['password']):
                        del existUser['password']
                        user = existUser
                        break
                else:
                    if self.username == existUser['username']:
                        del existUser['password']
                        user = existUser
                        break
        return user

    def getAllUsers(self):
        userList = []
        with open('./datas/userList.txt') as f:
            for line in f.readlines():
                userList.append(ast.literal_eval(line))
        return userList
            
    def isInvited(self):
        isInvited = False
        with open('./datas/inviteCodes.txt', 'r') as f:
            originList = ast.literal_eval(f.read())
            for code in originList:
                if UserModel.inviteCode == str(code):
                    isInvited = True
                    originList.remove(code)
                    with open('./datas/inviteCodes.txt', 'w') as _f:
                        _f.write(str(originList))
                    break
        return isInvited


    def registration(self):
        if not self.getUser() and self.isInvited():
            with open('./datas/userList.txt', 'a+') as f:
                newUser = self.detail()
                newUser['password'] = UserModel.generate_hash(newUser['password'])
                f.write(str(newUser) + '\n')
                del newUser['password']
                return newUser
        elif self.getUser():
            return 'User was exist!'
        elif not self.isInvited():
            return 'Invite code error!'
