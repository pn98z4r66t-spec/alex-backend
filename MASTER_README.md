# Alex AI Workspace - Complete System

**A professional, AI-powered workspace with email management, task collaboration, file storage, and team communication.**

---

## 🎯 Project Overview

Alex AI Workspace is a full-stack application that combines:
- **AI Assistant** with specialized agents (Benchmarking, Persona Generation, Data Analysis, Report Writing)
- **Email Management** with priority sorting and AI summarization
- **Task Management** with sharing via email and AI-enabled task boards
- **File Storage** with drag-and-drop upload, preview, and AI analysis
- **Team Collaboration** with real-time messaging and status tracking
- **Reference Library** for documents and resources

---

## 📦 Repository Structure

### Frontend Repository
**URL**: https://github.com/pn98z4r66t-spec/alex-workspace

- React 19 + Vite
- Tailwind CSS for styling
- JWT authentication
- Drag-and-drop file uploads
- AI chat interface
- Task sharing modals
- File manager with preview

### Backend Repository
**URL**: https://github.com/pn98z4r66t-spec/alex-backend

- Flask 3.1 REST API
- SQLAlchemy ORM
- JWT authentication
- File upload/download
- AI integration (Ollama/LM Studio)
- Email invitation system
- Rate limiting & security

---

## ✨ Complete Feature List

### 🤖 AI Features
- [x] AI chat interface with context awareness
- [x] Pre-built agents (Benchmarking, Persona Generation, Data Analysis, Report Writing)
- [x] File content analysis (summarization, keywords, sentiment)
- [x] Task-specific AI assistance
- [x] Email summarization
- [x] Local AI model support (Ollama, LM Studio, GPT4All)

### 📧 Email Management
- [x] Priority email inbox
- [x] Non-urgent email queue with AI summarization
- [x] Timer-based review reminders
- [x] Email-based task assignment
- [x] Professional HTML email templates

### 📋 Task Management
- [x] Task board with status tracking (To Do, In Progress, Done)
- [x] Urgency indicators and deadlines
- [x] Supervisor, assignee, and collaborator assignment
- [x] Task sharing via email with unique links
- [x] Permission levels (View, Edit, Admin)
- [x] AI-enabled shared task boards (no account required)
- [x] Expiring share links with revocation
- [x] Access tracking and analytics

### 📁 File Storage
- [x] Drag-and-drop file upload
- [x] Bulk file upload
- [x] File categories (Images, Documents, Spreadsheets, Media, Code, Archives)
- [x] Thumbnail generation for images
- [x] File preview (images, PDFs)
- [x] Text extraction from documents
- [x] AI-powered file analysis
- [x] Download tracking
- [x] Public/private file access control
- [x] Task-specific file attachments
- [x] Search and filter

### 👥 Team Collaboration
- [x] Team member list with online status
- [x] Direct messaging
- [x] Task assignment and collaboration
- [x] Shared task boards

### 🔒 Security Features
- [x] JWT authentication with refresh tokens
- [x] Password hashing (werkzeug)
- [x] Input validation (Marshmallow)
- [x] XSS protection (bleach)
- [x] SQL injection prevention
- [x] CORS restrictions
- [x] Rate limiting (200/day, 50/hour)
- [x] Secure file upload with type validation
- [x] File hash verification (SHA256)
- [x] Token-based file access

---

## 🚀 Quick Start

### Prerequisites
- Node.js 18+ and pnpm
- Python 3.11+
- Ollama or LM Studio (for local AI)
- SMTP server (optional, for email invitations)

### Frontend Setup

```bash
# Clone the repository
git clone https://github.com/pn98z4r66t-spec/alex-workspace.git
cd alex-workspace

# Install dependencies
pnpm install

# Create .env file
cat > .env << EOF
VITE_API_URL=http://localhost:5000/api
EOF

# Start development server
pnpm run dev

# Access at http://localhost:5173
```

### Backend Setup

```bash
# Clone the repository
git clone https://github.com/pn98z4r66t-spec/alex-backend.git
cd alex-backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cat > .env << EOF
FLASK_ENV=development
SECRET_KEY=your-secret-key-change-this
DATABASE_URL=sqlite:///alex.db
JWT_SECRET_KEY=your-jwt-secret-change-this

# AI Configuration
AI_API_URL=http://localhost:11434/api/generate
AI_MODEL=phi3

# Email Configuration (optional)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
FROM_EMAIL=noreply@alex.local
FRONTEND_URL=http://localhost:5173

# File Upload Configuration
UPLOAD_FOLDER=uploads
MAX_FILE_SIZE=52428800
EOF

# Run the application
python src/main.py

# Access at http://localhost:5000
```

### AI Setup (Ollama)

```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Pull a model (recommended: phi3 for laptops)
ollama pull phi3

# Ollama runs automatically at http://localhost:11434
```

---

## 📖 Documentation

### Complete Documentation Files

1. **IMPROVEMENTS_README.md** - Security improvements and v2.0 features
2. **TASK_SHARING_FEATURE.md** - Email-based task assignment documentation
3. **FILE_STORAGE_FEATURE.md** - File management system documentation
4. **CODE_REVIEW.md** - Security audit and code quality review
5. **FINAL_REVIEW.md** - UI accessibility checklist
6. **LOCAL_LAPTOP_SETUP_GUIDE.md** - Running everything on your laptop
7. **QUICK_REFERENCE.md** - Command cheat sheet

### API Documentation

#### Authentication
- `POST /api/auth/register` - Create new user
- `POST /api/auth/login` - Login and get tokens
- `POST /api/auth/logout` - Logout
- `POST /api/auth/refresh` - Refresh access token
- `GET /api/auth/me` - Get current user

#### Tasks
- `GET /api/tasks` - List all tasks (with pagination)
- `POST /api/tasks` - Create new task
- `GET /api/tasks/{id}` - Get task details
- `PUT /api/tasks/{id}` - Update task
- `DELETE /api/tasks/{id}` - Delete task
- `PATCH /api/tasks/{id}/status` - Update task status

#### Task Sharing
- `POST /api/tasks/share` - Share task via email
- `GET /api/tasks/access/{token}` - Access shared task (public)
- `PUT /api/tasks/update/{token}` - Update shared task (public)
- `DELETE /api/tasks/revoke/{token}` - Revoke share link
- `GET /api/tasks/list/{id}` - List all shares for a task

#### Files
- `GET /api/files/list` - List files (with filters)
- `POST /api/files/upload` - Upload single file
- `POST /api/files/bulk-upload` - Upload multiple files
- `GET /api/files/{id}` - Get file info
- `GET /api/files/download/{id}` - Download file
- `GET /api/files/preview/{id}` - Preview file
- `GET /api/files/thumbnail/{id}` - Get thumbnail
- `DELETE /api/files/{id}` - Delete file
- `POST /api/files/{id}/ai-analyze` - AI analysis of file

#### AI
- `POST /api/ai/chat` - Chat with AI
- `POST /api/ai/agents/{name}` - Execute specific agent
- `POST /api/ai/summarize` - Summarize content
- `POST /api/ai/analyze` - Analyze content
- `GET /api/ai/health` - Check AI availability

---

## 🎨 UI Components

### Frontend Components

```
src/
├── components/
│   ├── auth/
│   │   ├── LoginPage.jsx          # Login interface
│   │   └── RegisterPage.jsx       # Registration interface
│   ├── common/
│   │   ├── Header.jsx              # Top navigation bar
│   │   └── LoadingSpinner.jsx      # Loading indicator
│   ├── modals/
│   │   └── TaskShareModal.jsx      # Task sharing dialog
│   ├── LeftPanel.jsx               # Email & reference files
│   ├── CenterPanel.jsx             # AI chat interface
│   ├── RightPanel.jsx              # Task board & team
│   ├── SharedTaskBoard.jsx         # Public task board
│   └── FileManager.jsx             # File upload/management
├── context/
│   └── AuthContext.jsx             # Authentication state
├── services/
│   └── api.js                      # API client
└── App.jsx                         # Main application
```

### Backend Routes

```
src/
├── routes/
│   ├── auth.py                     # Authentication endpoints
│   ├── tasks.py                    # Task management
│   ├── task_sharing.py             # Task sharing & email
│   ├── files.py                    # File storage
│   └── ai.py                       # AI integration
├── models/
│   └── models.py                   # Database models
├── middleware/
│   └── auth.py                     # JWT middleware
├── utils/
│   ├── validation.py               # Input validation
│   └── errors.py                   # Error handling
└── config/
    └── config.py                   # Configuration
```

---

## 🔧 Configuration

### Environment Variables

#### Frontend (.env)
```env
VITE_API_URL=http://localhost:5000/api
```

#### Backend (.env)
```env
# Flask
FLASK_ENV=development
SECRET_KEY=your-secret-key
DATABASE_URL=sqlite:///alex.db

# JWT
JWT_SECRET_KEY=your-jwt-secret
JWT_ACCESS_TOKEN_EXPIRES=3600
JWT_REFRESH_TOKEN_EXPIRES=2592000

# AI
AI_API_URL=http://localhost:11434/api/generate
AI_MODEL=phi3

# Email
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
FROM_EMAIL=noreply@alex.local
FRONTEND_URL=http://localhost:5173

# Files
UPLOAD_FOLDER=uploads
MAX_FILE_SIZE=52428800

# CORS
CORS_ORIGINS=http://localhost:5173,http://localhost:5174

# Rate Limiting
RATELIMIT_STORAGE_URL=memory://
```

---

## 🧪 Testing

### Default Login Credentials

```
Email: admin@alex.local
Password: admin123
```

### Test File Upload

```bash
# Using cURL
curl -X POST http://localhost:5000/api/files/upload \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@test.pdf" \
  -F "description=Test document"
```

### Test Task Sharing

```bash
# Share a task
curl -X POST http://localhost:5000/api/tasks/share \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "task_id": 1,
    "emails": ["colleague@example.com"],
    "permission": "edit",
    "expires_in_days": 30
  }'
```

---

## 🎯 Use Cases

### 1. External Contractor Workflow
1. Create task in main interface
2. Click "Share" and enter contractor email
3. Set "Edit" permission
4. Contractor receives email with link
5. Contractor accesses AI-enabled task board
6. Updates status and adds notes
7. Track progress in main interface

### 2. Client Collaboration
1. Upload project files
2. Create task for client review
3. Share task with "View" permission
4. Client accesses task board
5. Client uses AI to ask questions
6. Client provides feedback via notes

### 3. Team File Sharing
1. Drag and drop files into File Manager
2. AI analyzes document content
3. Attach files to specific tasks
4. Team members download and preview
5. Track file access and downloads

---

## 🚀 Deployment

### Frontend (Vercel/Netlify)

```bash
# Build for production
pnpm run build

# Deploy dist/ folder
```

### Backend (Railway/Render/Heroku)

```bash
# Set environment variables in platform
# Deploy from GitHub repository
# Ensure uploads/ directory is persistent
```

### Database Migration

```bash
# Initialize database
python -c "from src.main import create_app, db; app = create_app(); app.app_context().push(); db.create_all()"
```

---

## 📊 System Requirements

### Minimum (Development)
- 8GB RAM
- 10GB disk space
- Dual-core processor

### Recommended (Production)
- 16GB RAM
- 50GB disk space (for file storage)
- Quad-core processor
- SSD storage

### AI Model Requirements
- **phi3** (3GB) - 8GB RAM minimum
- **mistral** (4GB) - 16GB RAM recommended
- **llama3.2** (7GB) - 16GB RAM minimum

---

## 🤝 Contributing

This is a personal project, but feel free to:
1. Fork the repositories
2. Create feature branches
3. Submit pull requests
4. Report issues

---

## 📝 License

MIT License - See LICENSE file in each repository

---

## 🙏 Acknowledgments

- **React** - UI framework
- **Flask** - Backend framework
- **Tailwind CSS** - Styling
- **Ollama** - Local AI inference
- **Lucide** - Icon library

---

## 📞 Support

For issues or questions:
1. Check documentation files
2. Review GitHub issues
3. Submit new issue with details

---

## 🗺️ Roadmap

### Completed ✅
- [x] AI chat interface with agents
- [x] Email management system
- [x] Task management and sharing
- [x] File storage with AI analysis
- [x] Team collaboration
- [x] Security hardening
- [x] Local AI integration

### Planned 🔮
- [ ] Real-time WebSocket updates
- [ ] Calendar integration
- [ ] Mobile app (React Native)
- [ ] Slack/Teams integration
- [ ] Advanced analytics dashboard
- [ ] Custom AI agent creation
- [ ] Voice commands
- [ ] Multi-language support

---

## 📸 Screenshots

See the visual mockups in the repository for:
- Login page
- Main workspace (3-panel layout)
- Task sharing modal
- Shared task board
- File manager

---

## 🎓 Learning Resources

### Technologies Used
- **Frontend**: React, Vite, Tailwind CSS, React Router
- **Backend**: Flask, SQLAlchemy, Flask-JWT-Extended
- **Database**: SQLite (development), PostgreSQL (production recommended)
- **AI**: Ollama, OpenAI-compatible APIs
- **Security**: JWT, bcrypt, CORS, rate limiting

### Key Concepts
- RESTful API design
- JWT authentication
- File upload handling
- AI integration patterns
- Email templating
- Token-based sharing
- Drag-and-drop interfaces

---

## 💡 Tips & Tricks

### Performance
- Use pagination for large file lists
- Enable database indexing
- Compress uploaded images
- Cache AI responses
- Use CDN for static assets

### Security
- Rotate JWT secrets regularly
- Use HTTPS in production
- Validate all file uploads
- Sanitize user inputs
- Monitor rate limits

### AI Optimization
- Use smaller models for faster responses
- Cache common queries
- Limit context window size
- Batch AI requests when possible

---

**Built with ❤️ for modern productivity**

Last Updated: October 11, 2025
Version: 2.0.0

