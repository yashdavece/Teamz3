
from flask import Flask, request, jsonify, send_from_directory
from flask_socketio import SocketIO, emit, join_room, leave_room
import json
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*")

def save_teams(teams_data):
    with open('teams.json', 'w') as f:
        json.dump(teams_data, f)

def load_teams():
    if os.path.exists('teams.json'):
        with open('teams.json', 'r') as f:
            return json.load(f)
    return {}

@app.route('/')
def serve_index():
    return send_from_directory('.', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('.', path)

@app.route('/api/teams', methods=['POST'])
def create_team():
    teams = load_teams()
    data = request.json
    teams[data['code']] = {
        'name': data['name'],
        'description': data['description'],
        'category': data['category'],
        'leader': data['leader'],
        'members': data['members']
    }
    save_teams(teams)
    return jsonify({'success': True})

@app.route('/api/teams/<team_code>')
def get_team(team_code):
    teams = load_teams()
    if team_code in teams:
        return jsonify(teams[team_code])
    return jsonify({'error': 'Team not found'}), 404

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
    print(f"Message received: {data}")
    room = data['team']
    emit('message', {'username': data['username'], 'message': data['message']}, to=room)

@socketio.on('discussion')
def handle_discussion(data):
    room = data['team']
    emit('discussion', data, room=room)

@socketio.on('material')
def handle_material(data):
    room = data['team']
    emit('material', data, room=room)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=3000, allow_unsafe_werkzeug=True, use_reloader=True, log_output=True)
