import functools

from flask_restful import Resource, reqparse
from flask import request
from flask_jwt_extended import jwt_required, decode_token
import random
from .. import mongo

inviteCodes = mongo.db.inviteCodes

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
        objId = inviteCodes.find_one({})['_id']
        codesList = inviteCodes.find_one({})['list']

        for i in range(4):
            newCode += str(random.randint(0, 9))
        codesList.append(newCode)

        inviteCodes.update({ '_id': objId }, { '$set': {'list': codesList} })
        
        return {
            'inviteCodesList': codesList,
            'newCode': newCode
        }

