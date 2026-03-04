# Flask Backend API
# Save this as backend/flask/app.py

from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import json

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend access

# In-memory storage (replace with database in production)
users = []
posts = []
contacts = []

# ===== ROUTES =====

@app.route('/')
def home():
    return jsonify({
        "message": "Welcome to WebDev Course API",
        "version": "1.0.0",
        "endpoints": [
            "/api/users",
            "/api/posts",
            "/api/contact",
            "/api/weather"
        ]
    })

# ===== USERS =====

@app.route('/api/users', methods=['GET'])
def get_users():
    return jsonify({"success": True, "data": users})

@app.route('/api/users', methods=['POST'])
def create_user():
    data = request.get_json()
    
    # Validation
    if not data or 'name' not in data or 'email' not in data:
        return jsonify({
            "success": False, 
            "error": "Name and email are required"
        }), 400
    
    user = {
        "id": len(users) + 1,
        "name": data['name'],
        "email": data['email'],
        "created_at": datetime.now().isoformat()
    }
    users.append(user)
    
    return jsonify({"success": True, "data": user}), 201

@app.route('/api/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = next((u for u in users if u['id'] == user_id), None)
    if not user:
        return jsonify({"success": False, "error": "User not found"}), 404
    return jsonify({"success": True, "data": user})

@app.route('/api/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    user = next((u for u in users if u['id'] == user_id), None)
    if not user:
        return jsonify({"success": False, "error": "User not found"}), 404
    
    data = request.get_json()
    user['name'] = data.get('name', user['name'])
    user['email'] = data.get('email', user['email'])
    
    return jsonify({"success": True, "data": user})

@app.route('/api/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    global users
    users = [u for u in users if u['id'] != user_id]
    return jsonify({"success": True, "message": "User deleted"})

# ===== CONTACT FORM =====

@app.route('/api/contact', methods=['POST'])
def submit_contact():
    data = request.get_json()
    
    # Validation
    required = ['name', 'email', 'message']
    for field in required:
        if not data or field not in data:
            return jsonify({
                "success": False,
                "error": f"{field} is required"
            }), 400
    
    contact = {
        "id": len(contacts) + 1,
        "name": data['name'],
        "email": data['email'],
        "message": data['message'],
        "submitted_at": datetime.now().isoformat()
    }
    contacts.append(contact)
    
    return jsonify({
        "success": True,
        "message": "Thank you! We will get back to you soon.",
        "data": contact
    }), 201

# ===== WEATHER (Mock) =====

@app.route('/api/weather', methods=['GET'])
def get_weather():
    city = request.args.get('city', 'London')
    
    # Mock weather data
    weather_data = {
        "city": city,
        "temperature": 22,
        "condition": "Sunny",
        "humidity": 65,
        "wind_speed": 12,
        "forecast": [
            {"day": "Today", "temp": 22, "condition": "Sunny"},
            {"day": "Tomorrow", "temp": 20, "condition": "Cloudy"},
            {"day": "Wednesday", "temp": 18, "condition": "Rainy"}
        ]
    }
    
    return jsonify({"success": True, "data": weather_data})

# ===== ERROR HANDLERS =====

@app.errorhandler(404)
def not_found(error):
    return jsonify({"success": False, "error": "Endpoint not found"}), 404

@app.errorhandler(500)
def server_error(error):
    return jsonify({"success": False, "error": "Internal server error"}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)