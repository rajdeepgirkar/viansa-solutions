from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from pymongo import MongoClient
from bson.objectid import ObjectId
import os
import datetime
import re

app = Flask(__name__, static_folder='../static')
CORS(app)

# MongoDB connection
client = MongoClient(os.environ.get("MONGO_URL"))
db = client["viansa"]
contacts_col = db["contacts"]

# Static Pages Routes
@app.route('/')
def serve_index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/admin')
def serve_admin():
    return send_from_directory(app.static_folder, 'admin.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory(app.static_folder, path)


# API Routes
@app.route('/api/contact', methods=['POST'])
def create_contact():
    data = request.get_json()

    if not data:
        return jsonify({"error": "No data provided"}), 400

    name = data.get("name", "").strip()
    email = data.get("email", "").strip()
    phone = data.get("phone", "").strip()
    service = data.get("service", "").strip()
    message = data.get("message", "").strip()

    # Validation
    if len(name) < 2:
        return jsonify({"error": "Name must be at least 2 characters"}), 400

    if len(phone) != 10:
        return jsonify({"error": "Enter valid phone number"}), 400

    email_regex = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'
    if not re.match(email_regex, email):
        return jsonify({"error": "Invalid email address"}), 400

    if len(message) < 10:
        return jsonify({"error": "Message must be at least 10 characters"}), 400

    contact = {
        "name": name,
        "email": email,
        "phone": phone,
        "service": service,
        "message": message,
        "time": datetime.datetime.utcnow(),
        "status": "incomplete"
    }

    try:
        result = contacts_col.insert_one(contact)
        return jsonify({
            "message": "Saved successfully",
            "id": str(result.inserted_id)
        }), 201

    except Exception as e:
        return jsonify({"error": "Server error"}), 500


@app.route('/api/admin/contacts', methods=['GET'])
def get_contacts():
    contacts = []
    for c in contacts_col.find().sort("time", -1):
        c["id"] = str(c["_id"])
        del c["_id"]
        c["time"] = c["time"].isoformat()
        contacts.append(c)
    return jsonify(contacts)


@app.route('/api/admin/contacts/<id>/status', methods=['PUT'])
def update_status(id):
    data = request.json
    status = data.get("status")

    if status not in ["completed", "incomplete"]:
        return jsonify({"error": "Invalid status"}), 400

    contacts_col.update_one(
        {"_id": ObjectId(id)},
        {"$set": {"status": status}}
    )

    return jsonify({"message": "Status updated"})


@app.route('/api/admin/contacts/<id>', methods=['DELETE'])
def delete_contact(id):
    contacts_col.delete_one({"_id": ObjectId(id)})
    return jsonify({"message": "Deleted"})


print("Mongo URL loaded:", bool(os.environ.get("MONGO_URL")))
