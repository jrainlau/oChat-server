from flask_restful import Resource, reqparse
import werkzeug
import functools
from flask import request
from flask_jwt_extended import jwt_required, decode_token
import random
import ast

def authenticatedOnly(f):
    @functools.wraps(f)
    def wrapped(*args, **kwargs):
        if (decode_token(request.args.get('token'))['identity'] == 'KingOfTheWorld'):
            return f(*args, **kwargs)
        else:
            return 401
    return wrapped

class GenerateInviteCode(Resource):
    @authenticatedOnly
    def get(self):
        newCode = ''
        originList = []
        for i in range(4):
            newCode += str(random.randint(0, 9))
        with open('./datas/inviteCodes.txt', 'r') as f:
            originList = ast.literal_eval(f.read())
            originList.append(newCode)
        with open('./datas/inviteCodes.txt', 'w') as f:
            f.write(str(originList))
        return {
            'inviteCodesList': originList,
            'newCode': newCode
        }

