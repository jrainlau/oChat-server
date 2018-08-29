from .. import app, socketio
from flask import jsonify

@app.route('/')
def index():
    return jsonify({
        'message': 'Hello, World!'
    })
