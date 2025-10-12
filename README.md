# Alex Backend - AI Workspace API

![Version](https://img.shields.io/badge/version-2.0.0-blue)
![Python](https://img.shields.io/badge/python-3.11+-green)
![Flask](https://img.shields.io/badge/Flask-3.1.1-black)
![Security](https://img.shields.io/badge/security-A+-brightgreen)

Enterprise-grade Flask API backend for Alex AI Workspace with JWT authentication, input validation, and comprehensive security features.

## ✨ Features

- 🔒 **JWT Authentication** - Secure token-based auth
- ✅ **Input Validation** - Marshmallow schemas
- 🛡️ **Security** - Rate limiting, CORS, XSS protection
- 📊 **Pagination** - Efficient data retrieval
- 🤖 **AI Integration** - Ollama/LM Studio support
- 📝 **Logging** - Rotating file logs
- ⚡ **Performance** - Database indexing & connection pooling

## 🚀 Quick Start

```bash
# Clone repository
git clone https://github.com/yourusername/alex-backend.git
cd alex-backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env

# Run server
python src/main.py
```

Server runs on **http://localhost:5000**

## 🔐 Default Credentials

```
Email: admin@alex.local
Password: admin123
```

## 📋 API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login
- `POST /api/auth/logout` - Logout
- `POST /api/auth/refresh` - Refresh token
- `GET /api/auth/me` - Get current user

### Tasks
- `GET /api/tasks` - List tasks (paginated)
- `GET /api/tasks/:id` - Get task
- `POST /api/tasks` - Create task
- `PUT /api/tasks/:id` - Update task
- `DELETE /api/tasks/:id` - Delete task
- `PATCH /api/tasks/:id/status` - Update status

### AI
- `POST /api/ai/chat` - Chat with AI
- `POST /api/ai/agents/:name` - Execute agent
- `POST /api/ai/summarize` - Summarize content
- `POST /api/ai/analyze` - Analyze content
- `GET /api/ai/health` - Check AI service

## 🔧 Configuration

Create `.env` file:

```env
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret
FLASK_ENV=development
DATABASE_URL=sqlite:///src/database/app.db
CORS_ORIGINS=http://localhost:5173
AI_API_URL=http://localhost:11434/api/generate
AI_MODEL=phi3
```

## 📦 Dependencies

```txt
Flask==3.1.1
Flask-SQLAlchemy==3.1.1
Flask-CORS==6.0.0
Flask-JWT-Extended==4.6.0
Flask-Limiter==3.8.0
marshmallow==3.23.2
bleach==6.2.0
requests==2.32.3
python-dotenv==1.0.1
```

## 🧪 Testing

```bash
# Test authentication
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@alex.local","password":"admin123"}'

# Test tasks (with token)
curl http://localhost:5000/api/tasks \
  -H "Authorization: Bearer <your-token>"
```

## 🏗️ Project Structure

```
alex-backend/
├── src/
│   ├── config/
│   │   └── config.py          # Configuration
│   ├── middleware/
│   │   └── auth.py            # JWT middleware
│   ├── models/
│   │   └── models.py          # Database models
│   ├── routes/
│   │   ├── auth.py            # Auth endpoints
│   │   ├── tasks.py           # Task endpoints
│   │   └── ai.py              # AI endpoints
│   ├── utils/
│   │   ├── validation.py      # Input validation
│   │   └── errors.py          # Error handling
│   └── main.py                # Application entry
├── requirements.txt
├── .env.example
└── README.md
```

## 🔒 Security Features

- ✅ JWT authentication
- ✅ Password hashing
- ✅ Input validation
- ✅ XSS protection
- ✅ SQL injection prevention
- ✅ CORS restrictions
- ✅ Rate limiting
- ✅ Secure session cookies

## 📄 License

MIT License

## 📧 Contact

- Backend: [https://github.com/yourusername/alex-backend](https://github.com/yourusername/alex-backend)
- Frontend: [https://github.com/yourusername/alex-workspace](https://github.com/yourusername/alex-workspace)

---

**Made with ❤️ by Manus AI**  
**Version**: 2.0.0 | **Status**: Production Ready

