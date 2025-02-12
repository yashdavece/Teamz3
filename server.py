from flask import Flask, request, jsonify
import os
import json
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

# User storage
USERS_FILE = 'users.json'

def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f)

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    first_name = data.get('firstName')
    last_name = data.get('lastName')
    role = data.get('role')

    if not all([first_name, last_name, role]):
        return jsonify({'error': 'All fields are required'}), 400

    user_id = f"{first_name.lower()}_{last_name.lower()}"
    users = load_users()
    users[user_id] = {
        'firstName': first_name,
        'lastName': last_name,
        'role': role
    }
    save_users(users)

    return jsonify({'message': 'Login successful'})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=3000)