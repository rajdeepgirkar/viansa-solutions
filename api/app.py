from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import json
import datetime

app = Flask(__name__, static_folder='../static')
CORS(app)

# DATA_FILE = os.path.join(os.path.dirname(__file__), '../data/contacts.json')
DATA_FILE = '/tmp/contacts.json'

def load_data():
    if not os.path.exists(DATA_FILE):
        return []
    try:
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    except:
        return []

# def save_data(data):
#     os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
#     with open(DATA_FILE, 'w') as f:
#         json.dump(data, f, indent=2)

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)

@app.route('/')
def serve_index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/admin')
def serve_admin():
    return send_from_directory(app.static_folder, 'admin.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory(app.static_folder, path)

@app.route('/api/contact', methods=['POST'])
def contact():
    data = request.json
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    contacts = load_data()
    new_contact = {
        "id": len(contacts) + 1,
        "name": data.get('name'),
        "email": data.get('email'),
        "phone": data.get('phone'),
        "service": data.get('service'),
        "message": data.get('message'),
        "time": datetime.datetime.now().isoformat(),
        "status": "incomplete"
    }
    contacts.append(new_contact)
    save_data(contacts)
    return jsonify({"message": "Contact saved successfully", "id": new_contact["id"]}), 201

@app.route('/api/admin/contacts', methods=['GET'])
def get_contacts():
    contacts = load_data()
    return jsonify(contacts)

# if __name__ == '__main__':
#     # Ensure data directory exists
#     os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
#     if not os.path.exists(DATA_FILE):
#         with open(DATA_FILE, 'w') as f:
#             json.dump([], f)
            
#     app.run(host='0.0.0.0', port=5000)
