
from flask import Flask, request, jsonify, send_from_directory
import json
import os

app = Flask(__name__)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=3000)
