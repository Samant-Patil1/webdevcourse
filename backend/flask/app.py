# Flask Backend API - Complete Implementation
# Run with: python app.py
# Requires: pip install flask flask-cors flask-jwt-extended python-dotenv

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
from functools import wraps
import os
import sqlite3
import json

# Initialize Flask app
app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-change-in-production')
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'jwt-secret-key-change-in-production')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Enable CORS for all routes
CORS(app, resources={
    r"/api/*": {
        "origins": ["*"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# Initialize JWT
jwt = JWTManager(app)

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Database setup
def get_db_connection():
    """Create a database connection"""
    conn = sqlite3.connect('webdev_course.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize the database with tables"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT DEFAULT 'user',
            avatar TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Posts table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            author_id INTEGER NOT NULL,
            tags TEXT,
            published BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (author_id) REFERENCES users (id)
        )
    ''')
    
    # Comments table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS comments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            post_id INTEGER NOT NULL,
            author_id INTEGER NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (post_id) REFERENCES posts (id) ON DELETE CASCADE,
            FOREIGN KEY (author_id) REFERENCES users (id)
        )
    ''')
    
    # Contact messages table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS contacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            subject TEXT,
            message TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✅ Database initialized successfully!")

# Initialize database on startup
init_db()

# Helper functions
def allowed_file(filename):
    """Check if file extension is allowed"""
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'txt', 'doc', 'docx'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def validate_json(*required_fields):
    """Decorator to validate required JSON fields"""
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if not request.is_json:
                return jsonify({"error": "Content-Type must be application/json"}), 400
            
            data = request.get_json()
            missing_fields = [field for field in required_fields if field not in data]
            
            if missing_fields:
                return jsonify({
                    "error": "Missing required fields",
                    "missing": missing_fields
                }), 400
            
            return f(*args, **kwargs)
        return wrapper
    return decorator

# ============================================
# AUTHENTICATION ROUTES
# ============================================

@app.route('/api/auth/register', methods=['POST'])
@validate_json('username', 'email', 'password')
def register():
    """Register a new user"""
    data = request.get_json()
    
    username = data['username'].strip()
    email = data['email'].strip().lower()
    password = data['password']
    
    # Validation
    if len(username) < 3:
        return jsonify({"error": "Username must be at least 3 characters"}), 400
    
    if len(password) < 6:
        return jsonify({"error": "Password must be at least 6 characters"}), 400
    
    if '@' not in email:
        return jsonify({"error": "Invalid email address"}), 400
    
    # Hash password
    password_hash = generate_password_hash(password)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            'INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)',
            (username, email, password_hash)
        )
        conn.commit()
        user_id = cursor.lastrowid
        
        # Generate token
        access_token = create_access_token(identity=user_id)
        
        return jsonify({
            "message": "User registered successfully",
            "user": {
                "id": user_id,
                "username": username,
                "email": email
            },
            "access_token": access_token
        }), 201
        
    except sqlite3.IntegrityError as e:
        if 'username' in str(e):
            return jsonify({"error": "Username already exists"}), 409
        return jsonify({"error": "Email already exists"}), 409
    finally:
        conn.close()

@app.route('/api/auth/login', methods=['POST'])
@validate_json('email', 'password')
def login():
    """Login user and return JWT token"""
    data = request.get_json()
    
    email = data['email'].strip().lower()
    password = data['password']
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
    user = cursor.fetchone()
    conn.close()
    
    if user and check_password_hash(user['password_hash'], password):
        access_token = create_access_token(identity=user['id'])
        return jsonify({
            "message": "Login successful",
            "user": {
                "id": user['id'],
                "username": user['username'],
                "email": user['email'],
                "role": user['role'],
                "avatar": user['avatar']
            },
            "access_token": access_token
        })
    
    return jsonify({"error": "Invalid email or password"}), 401

@app.route('/api/auth/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """Get current logged-in user info"""
    user_id = get_jwt_identity()
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        'SELECT id, username, email, role, avatar, created_at FROM users WHERE id = ?',
        (user_id,)
    )
    user = cursor.fetchone()
    conn.close()
    
    if user:
        return jsonify({
            "user": dict(user)
        })
    
    return jsonify({"error": "User not found"}), 404

# ============================================
# USERS ROUTES
# ============================================

@app.route('/api/users', methods=['GET'])
def get_users():
    """Get all users (public)"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Pagination
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    offset = (page - 1) * per_page
    
    cursor.execute(
        'SELECT id, username, email, avatar, created_at FROM users LIMIT ? OFFSET ?',
        (per_page, offset)
    )
    users = cursor.fetchall()
    
    cursor.execute('SELECT COUNT(*) as count FROM users')
    total = cursor.fetchone()['count']
    
    conn.close()
    
    return jsonify({
        "users": [dict(user) for user in users],
        "pagination": {
            "page": page,
            "per_page": per_page,
            "total": total,
            "pages": (total + per_page - 1) // per_page
        }
    })

@app.route('/api/users/<id>', methods=['GET'])
def get_user(id):
    """Get a specific user by ID"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        'SELECT id, username, email, avatar, created_at FROM users WHERE id = ?',
        (id,)
    )
    user = cursor.fetchone()
    conn.close()
    
    if user:
        return jsonify({"user": dict(user)})
    
    return jsonify({"error": "User not found"}), 404

@app.route('/api/users/<id>', methods=['PUT'])
@jwt_required()
def update_user(id):
    """Update user (only own profile or admin)"""
    current_user_id = get_jwt_identity()
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if user exists
    cursor.execute('SELECT * FROM users WHERE id = ?', (id,))
    user = cursor.fetchone()
    
    if not user:
        conn.close()
        return jsonify({"error": "User not found"}), 404
    
    # Check permissions
    cursor.execute('SELECT role FROM users WHERE id = ?', (current_user_id,))
    current_user = cursor.fetchone()
    
    if str(current_user_id) != str(id) and current_user['role'] != 'admin':
        conn.close()
        return jsonify({"error": "Unauthorized"}), 403
    
    data = request.get_json()
    updates = []
    values = []
    
    if 'username' in data:
        updates.append('username = ?')
        values.append(data['username'])
    
    if 'avatar' in data:
        updates.append('avatar = ?')
        values.append(data['avatar'])
    
    if updates:
        values.append(id)
        query = f"UPDATE users SET {', '.join(updates)}, updated_at = CURRENT_TIMESTAMP WHERE id = ?"
        cursor.execute(query, values)
        conn.commit()
    
    conn.close()
    return jsonify({"message": "User updated successfully"})

@app.route('/api/users/<id>', methods=['DELETE'])
@jwt_required()
def delete_user(id):
    """Delete user (admin only or own account)"""
    current_user_id = get_jwt_identity()
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT role FROM users WHERE id = ?', (current_user_id,))
    current_user = cursor.fetchone()
    
    if str(current_user_id) != str(id) and current_user['role'] != 'admin':
        conn.close()
        return jsonify({"error": "Unauthorized"}), 403
    
    cursor.execute('DELETE FROM users WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    
    return jsonify({"message": "User deleted successfully"})

# ============================================
# POSTS ROUTES
# ============================================

@app.route('/api/posts', methods=['GET'])
def get_posts():
    """Get all posts with pagination and filtering"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Query parameters
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    author_id = request.args.get('author_id', type=int)
    published_only = request.args.get('published', 'true').lower() == 'true'
    
    offset = (page - 1) * per_page
    
    # Build query
    query = '''
        SELECT p.*, u.username as author_name, u.avatar as author_avatar
        FROM posts p
        JOIN users u ON p.author_id = u.id
        WHERE 1=1
    '''
    params = []
    
    if published_only:
        query += ' AND p.published = 1'
    
    if author_id:
        query += ' AND p.author_id = ?'
        params.append(author_id)
    
    query += ' ORDER BY p.created_at DESC LIMIT ? OFFSET ?'
    params.extend([per_page, offset])
    
    cursor.execute(query, params)
    posts = cursor.fetchall()
    
    # Get total count
    count_query = 'SELECT COUNT(*) as count FROM posts WHERE 1=1'
    count_params = []
    
    if published_only:
        count_query += ' AND published = 1'
    if author_id:
        count_query += ' AND author_id = ?'
        count_params.append(author_id)
    
    cursor.execute(count_query, count_params)
    total = cursor.fetchone()['count']
    
    conn.close()
    
    return jsonify({
        "posts": [dict(post) for post in posts],
        "pagination": {
            "page": page,
            "per_page": per_page,
            "total": total,
            "pages": (total + per_page - 1) // per_page
        }
    })

@app.route('/api/posts/<id>', methods=['GET'])
def get_post(id):
    """Get a single post with comments"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get post
    cursor.execute('''
        SELECT p.*, u.username as author_name, u.avatar as author_avatar
        FROM posts p
        JOIN users u ON p.author_id = u.id
        WHERE p.id = ?
    ''', (id,))
    post = cursor.fetchone()
    
    if not post:
        conn.close()
        return jsonify({"error": "Post not found"}), 404
    
    # Get comments
    cursor.execute('''
        SELECT c.*, u.username as author_name, u.avatar as author_avatar
        FROM comments c
        JOIN users u ON c.author_id = u.id
        WHERE c.post_id = ?
        ORDER BY c.created_at DESC
    ''', (id,))
    comments = cursor.fetchall()
    
    conn.close()
    
    post_dict = dict(post)
    post_dict['comments'] = [dict(comment) for comment in comments]
    
    return jsonify({"post": post_dict})

@app.route('/api/posts', methods=['POST'])
@jwt_required()
@validate_json('title', 'content')
def create_post():
    """Create a new post"""
    user_id = get_jwt_identity()
    data = request.get_json()
    
    title = data['title'].strip()
    content = data['content'].strip()
    tags = data.get('tags', '')
    published = data.get('published', False)
    
    if len(title) < 3:
        return jsonify({"error": "Title must be at least 3 characters"}), 400
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        'INSERT INTO posts (title, content, author_id, tags, published) VALUES (?, ?, ?, ?, ?)',
        (title, content, user_id, tags, published)
    )
    conn.commit()
    post_id = cursor.lastrowid
    conn.close()
    
    return jsonify({
        "message": "Post created successfully",
        "post": {
            "id": post_id,
            "title": title,
            "content": content,
            "author_id": user_id,
            "tags": tags,
            "published": published
        }
    }), 201

@app.route('/api/posts/<id>', methods=['PUT'])
@jwt_required()
def update_post(id):
    """Update a post"""
    user_id = get_jwt_identity()
    data = request.get_json()
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check ownership
    cursor.execute('SELECT author_id FROM posts WHERE id = ?', (id,))
    post = cursor.fetchone()
    
    if not post:
        conn.close()
        return jsonify({"error": "Post not found"}), 404
    
    cursor.execute('SELECT role FROM users WHERE id = ?', (user_id,))
    user = cursor.fetchone()
    
    if post['author_id'] != user_id and user['role'] != 'admin':
        conn.close()
        return jsonify({"error": "Unauthorized"}), 403
    
    # Update fields
    updates = []
    values = []
    
    for field in ['title', 'content', 'tags', 'published']:
        if field in data:
            updates.append(f'{field} = ?')
            values.append(data[field])
    
    if updates:
        values.append(id)
        query = f"UPDATE posts SET {', '.join(updates)}, updated_at = CURRENT_TIMESTAMP WHERE id = ?"
        cursor.execute(query, values)
        conn.commit()
    
    conn.close()
    return jsonify({"message": "Post updated successfully"})

@app.route('/api/posts/<id>', methods=['DELETE'])
@jwt_required()
def delete_post(id):
    """Delete a post"""
    user_id = get_jwt_identity()
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT author_id FROM posts WHERE id = ?', (id,))
    post = cursor.fetchone()
    
    if not post:
        conn.close()
        return jsonify({"error": "Post not found"}), 404
    
    cursor.execute('SELECT role FROM users WHERE id = ?', (user_id,))
    user = cursor.fetchone()
    
    if post['author_id'] != user_id and user['role'] != 'admin':
        conn.close()
        return jsonify({"error": "Unauthorized"}), 403
    
    cursor.execute('DELETE FROM posts WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    
    return jsonify({"message": "Post deleted successfully"})

# ============================================
# COMMENTS ROUTES
# ============================================

@app.route('/api/posts/<post_id>/comments', methods=['POST'])
@jwt_required()
@validate_json('content')
def create_comment(post_id):
    """Add a comment to a post"""
    user_id = get_jwt_identity()
    data = request.get_json()
    content = data['content'].strip()
    
    if len(content) < 1:
        return jsonify({"error": "Comment cannot be empty"}), 400
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if post exists
    cursor.execute('SELECT id FROM posts WHERE id = ?', (post_id,))
    if not cursor.fetchone():
        conn.close()
        return jsonify({"error": "Post not found"}), 404
    
    cursor.execute(
        'INSERT INTO comments (post_id, author_id, content) VALUES (?, ?, ?)',
        (post_id, user_id, content)
    )
    conn.commit()
    conn.close()
    
    return jsonify({"message": "Comment added successfully"}), 201

# ============================================
# CONTACT FORM
# ============================================

@app.route('/api/contact', methods=['POST'])
@validate_json('name', 'email', 'message')
def submit_contact():
    """Submit contact form"""
    data = request.get_json()
    
    name = data['name'].strip()
    email = data['email'].strip()
    subject = data.get('subject', '').strip()
    message = data['message'].strip()
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        'INSERT INTO contacts (name, email, subject, message) VALUES (?, ?, ?, ?)',
        (name, email, subject, message)
    )
    conn.commit()
    conn.close()
    
    return jsonify({
        "message": "Thank you! We will get back to you soon.",
        "data": {
            "name": name,
            "email": email,
            "subject": subject
        }
    }), 201

# ============================================
# FILE UPLOAD
# ============================================

@app.route('/api/upload', methods=['POST'])
@jwt_required()
def upload_file():
    """Upload a file"""
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
        unique_filename = timestamp + filename
        
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(filepath)
        
        return jsonify({
            "message": "File uploaded successfully",
            "filename": unique_filename,
            "url": f"/api/uploads/{unique_filename}"
        }), 201
    
    return jsonify({"error": "File type not allowed"}), 400

@app.route('/api/uploads/<filename>', methods=['GET'])
def get_upload(filename):
    """Serve uploaded files"""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# ============================================
# WEATHER API (Mock)
# ============================================

@app.route('/api/weather', methods=['GET'])
def get_weather():
    """Get weather data (mock)"""
    city = request.args.get('city', 'London')
    
    # Mock weather data - in production, use OpenWeatherMap API
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

# ============================================
# HOME ROUTE
# ============================================

@app.route('/')
def home():
    """API Home"""
    return jsonify({
        "message": "Welcome to WebDev Course API",
        "version": "1.0.0",
        "endpoints": {
            "auth": {
                "register": "POST /api/auth/register",
                "login": "POST /api/auth/login",
                "me": "GET /api/auth/me"
            },
            "users": {
                "list": "GET /api/users",
                "get": "GET /api/users/<id>",
                "update": "PUT /api/users/<id>",
                "delete": "DELETE /api/users/<id>"
            },
            "posts": {
                "list": "GET /api/posts",
                "get": "GET /api/posts/<id>",
                "create": "POST /api/posts",
                "update": "PUT /api/posts/<id>",
                "delete": "DELETE /api/posts/<id>"
            },
            "comments": {
                "create": "POST /api/posts/<post_id>/comments"
            },
            "contact": {
                "submit": "POST /api/contact"
            },
            "upload": {
                "upload": "POST /api/upload",
                "get": "GET /api/uploads/<filename>"
            },
            "weather": {
                "get": "GET /api/weather?city=<city>"
            }
        }
    })

# ============================================
# ERROR HANDLERS
# ============================================

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def server_error(error):
    return jsonify({"error": "Internal server error"}), 500

@app.errorhandler(400)
def bad_request(error):
    return jsonify({"error": "Bad request"}), 400

# ============================================
# MAIN
# ============================================

if __name__ == '__main__':
    print("🚀 Starting WebDev Course API Server...")
    print("📍 URL: http://localhost:5000")
    print("")
    print("Available endpoints:")
    print("  • GET  /                    - API info")
    print("  • POST /api/auth/register   - Register user")
    print("  • POST /api/auth/login      - Login user")
    print("  • GET  /api/users           - List users")
    print("  • GET  /api/posts           - List posts")
    print("  • POST /api/contact         - Submit contact form")
    print("")
    
    app.run(debug=True, host='0.0.0.0', port=5000)