
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from flask_socketio import SocketIO, emit, join_room, leave_room
import json
import os

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# File storage
TEAMS_FILE = 'teams.json'
MEMBERS_FILE = 'members.json'
MATERIALS_FILE = 'materials.json'
DISCUSSIONS_FILE = 'discussions.json'

def load_data(filename):
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            return json.load(f)
    return {}

def save_data(data, filename):
    with open(filename, 'w') as f:
        json.dump(data, f)

@app.route('/')
def serve_index():
    return send_from_directory('.', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('.', path)

@app.route('/api/teams', methods=['POST'])
def create_team():
    teams = load_data(TEAMS_FILE)
    data = request.json
    team_code = f"TEAM{len(teams) + 1}"
    teams[team_code] = {
        'name': data['teamName'],
        'description': data['teamDescription'],
        'category': data['teamCategory'],
        'leader': data['username']
    }
    members = load_data(MEMBERS_FILE)
    members[team_code] = [data['username']]
    save_data(teams, TEAMS_FILE)
    save_data(members, MEMBERS_FILE)
    return jsonify({'code': team_code})

@app.route('/api/teams/leader', methods=['POST'])
def change_leader():
    data = request.json
    team_code = data['teamCode']
    new_leader = data['newLeader']
    current_user = data['currentUser']
    
    teams = load_data(TEAMS_FILE)
    members = load_data(MEMBERS_FILE)
    
    if team_code not in teams or team_code not in members:
        return jsonify({'error': 'Team not found'}), 404
        
    if teams[team_code]['leader'] != current_user:
        return jsonify({'error': 'Only the team leader can change leadership'}), 403
        
    if new_leader not in members[team_code]:
        return jsonify({'error': 'New leader must be a team member'}), 400
        
    teams[team_code]['leader'] = new_leader
    save_data(teams, TEAMS_FILE)
    return jsonify({'message': 'Leadership transferred successfully'})

@app.route('/api/teams/join', methods=['POST'])
def join_team():
    members = load_data(MEMBERS_FILE)
    data = request.json
    team_code = data['teamCode']
    username = data['username']
    teams = load_data(TEAMS_FILE)
    
    if team_code not in teams:
        return jsonify({'error': 'Invalid team code'}), 404
    
    if team_code not in members:
        members[team_code] = []
    
    # Check if username already exists in the team
    if username in members[team_code]:
        return jsonify({'error': 'Username already exists in this team. Please choose a different username.'}), 400
    
    members[team_code].append(username)
    save_data(members, MEMBERS_FILE)
    return jsonify({'message': 'Joined successfully'})

@app.route('/api/teams/<team_code>')
def get_team(team_code):
    teams = load_data(TEAMS_FILE)
    members = load_data(MEMBERS_FILE)
    
    if team_code not in teams:
        return jsonify({'error': 'Team not found'}), 404
        
    team_data = teams[team_code]
    team_data['members'] = members.get(team_code, [])
    return jsonify(team_data)

@socketio.on('join')
def on_join(data):
    room = data['team']
    join_room(room)
    emit('message', {'username': 'System', 'message': f"{data['username']} has joined the team"}, room=room)

@socketio.on('message')
def on_message(data):
    room = data['team']
    emit('message', {'username': data['username'], 'message': data['message']}, room=room)

@socketio.on('discussion')
def on_discussion(data):
    room = data['team']
    discussions = load_data(DISCUSSIONS_FILE)
    if room not in discussions:
        discussions[room] = []
    discussions[room].append({
        'username': data['username'],
        'topic': data['topic'],
        'content': data['content']
    })
    save_data(discussions, DISCUSSIONS_FILE)
    emit('discussion', data, room=room)

@socketio.on('material')
def on_material(data):
    room = data['team']
    materials = load_data(MATERIALS_FILE)
    if room not in materials:
        materials[room] = []
    materials[room].append({
        'username': data['username'],
        'title': data['title'],
        'url': data['url']
    })
    save_data(materials, MATERIALS_FILE)
    emit('material', data, room=room)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=3000)
