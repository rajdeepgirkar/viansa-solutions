from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from pymongo import MongoClient
from bson.objectid import ObjectId
import os
import datetime

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
    data = request.json
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    contact = {
        "name": data.get('name'),
        "email": data.get('email'),
        "phone": data.get('phone'),
        "service": data.get('service'),
        "message": data.get('message'),
        "time": datetime.datetime.utcnow(),
        "status": "incomplete"
    }
    
    result = contacts_col.insert_one(contact)
    contact["id"] = str(result.inserted_id)
    
    return jsonify({"message": "Saved", "id": contact["id"]}), 201


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
