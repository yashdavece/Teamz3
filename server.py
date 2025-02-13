from flask import Flask, request, jsonify, send_from_directory
from flask_socketio import SocketIO, emit, join_room
import os
import json

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/api/teams', methods=['POST'])
def create_team():
    data = request.json
    team_code = data.get('code')
    
    if not team_code:
        return jsonify({"success": False, "error": "Team code is required"}), 400

    # Load existing teams
    if os.path.exists('teams.json'):
        with open('teams.json', 'r') as file:
            teams = json.load(file)
    else:
        teams = {}

    # Save new team
    teams[team_code] = data
    with open('teams.json', 'w') as file:
        json.dump(teams, file)

    return jsonify({"success": True, "data": data})

@socketio.on('connect')
def handle_connect():
    print("Client connected")

if __name__ == "__main__":
    from werkzeug.middleware.proxy_fix import ProxyFix
    app.wsgi_app = ProxyFix(app.wsgi_app)

    # Run with Gunicorn when deployed
    import gunicorn.app.base

    class Application(gunicorn.app.base.BaseApplication):
        def __init__(self, app, options=None):
            self.options = options or {}
            self.application = app
            super().__init__()

        def load_config(self):
            for key, value in self.options.items():
                self.cfg.set(key, value)

        def load(self):
            return self.application

    options = {
        "bind": "0.0.0.0:3000",
        "workers": 1,
        "timeout": 120
    }

    Application(app, options).run()