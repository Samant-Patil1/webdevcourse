# Flask Backend API

A comprehensive REST API built with Flask for the Web Development Course.

## Features

- ✅ User Authentication (JWT tokens)
- ✅ CRUD Operations for Users, Posts, Comments
- ✅ File Upload Support
- ✅ SQLite Database
- ✅ CORS Enabled
- ✅ Input Validation
- ✅ Error Handling
- ✅ Contact Form API
- ✅ Mock Weather API

## Installation

1. Navigate to the backend folder:
```bash
cd backend/flask
```

2. Create a virtual environment:
```bash
python -m venv venv
```

3. Activate the virtual environment:
- Windows: `venv\Scripts\activate`
- Mac/Linux: `source venv/bin/activate`

4. Install dependencies:
```bash
pip install -r requirements.txt
```

5. Run the server:
```bash
python app.py
```

The server will start at `http://localhost:5000`

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login user
- `GET /api/auth/me` - Get current user

### Users
- `GET /api/users` - List all users
- `GET /api/users/:id` - Get user by ID
- `PUT /api/users/:id` - Update user
- `DELETE /api/users/:id` - Delete user

### Posts
- `GET /api/posts` - List all posts
- `GET /api/posts/:id` - Get post by ID
- `POST /api/posts` - Create new post (auth required)
- `PUT /api/posts/:id` - Update post (auth required)
- `DELETE /api/posts/:id` - Delete post (auth required)

### Comments
- `POST /api/posts/:post_id/comments` - Add comment (auth required)

### Contact
- `POST /api/contact` - Submit contact form

### Upload
- `POST /api/upload` - Upload file (auth required)
- `GET /api/uploads/:filename` - Get uploaded file

### Weather
- `GET /api/weather?city=:city` - Get weather (mock)

## Environment Variables

Create a `.env` file:
```
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret
```

## Frontend Integration

The API is configured with CORS enabled, so you can call it from your frontend:

```javascript
// Register user
fetch('http://localhost:5000/api/auth/register', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    username: 'john',
    email: 'john@example.com',
    password: 'password123'
  })
});

// Login
fetch('http://localhost:5000/api/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    email: 'john@example.com',
    password: 'password123'
  })
});
```

## Database

SQLite is used for simplicity. The database file `webdev_course.db` is created automatically.

Tables:
- `users` - User accounts
- `posts` - Blog posts
- `comments` - Post comments
- `contacts` - Contact form submissions