
from flask import Flask, request, jsonify, send_from_directory
from flask_socketio import SocketIO, emit, join_room, leave_room
import json
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*")

@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('join')
def handle_join(data):
    room = data['team']
    join_room(room)
    emit('message', {'username': 'System', 'message': f"{data['username']} has joined the team"}, room=room)

@socketio.on('message')
def handle_message(data):
    room = data['team']
    emit('message', {'username': data['username'], 'message': data['message']}, room=room)

@socketio.on('discussion')
def handle_discussion(data):
    room = data['team']
    emit('discussion', data, room=room)

@socketio.on('material')
def handle_material(data):
    room = data['team']
    emit('material', data, room=room)

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=3000)
