# File Storage System - Complete Documentation

## Overview

The File Storage System provides native file management capabilities on the hosting server, allowing users and AI to upload, view, download, and analyze files directly within the Alex AI Workspace.

---

## ✨ Key Features

### 📤 **Upload Capabilities**
- Drag-and-drop file upload
- Bulk file upload (multiple files at once)
- Progress tracking
- File type validation
- Size limit enforcement (50MB default)
- Automatic thumbnail generation for images
- Text extraction for AI processing

### 📁 **File Management**
- Browse files by category
- Search files by name or description
- Filter by task assignment
- Preview images and PDFs
- Download files
- Delete files
- Track download counts

### 🤖 **AI Integration**
- Automatic text extraction from documents
- AI-powered file analysis (summary, keywords, sentiment)
- Context-aware file recommendations
- Content-based search

### 🔒 **Security & Access Control**
- User-based file ownership
- Public/private file access
- Task-specific file attachments
- Secure file hashing (SHA256)
- File type validation
- Size limits

---

## 📦 Supported File Types

### Images
- PNG, JPG, JPEG, GIF, WEBP, SVG
- Automatic thumbnail generation
- In-browser preview

### Documents
- PDF, DOC, DOCX, TXT, MD, RTF
- Text extraction for AI
- PDF preview in browser

### Spreadsheets
- XLS, XLSX, CSV
- Future: Data visualization

### Presentations
- PPT, PPTX
- Future: Slide preview

### Code Files
- PY, JS, HTML, CSS, JSON, XML, YAML, YML
- Syntax highlighting (future)
- Text extraction

### Media
- MP3, MP4, WAV, AVI, MOV
- Future: Media player integration

### Archives
- ZIP, TAR, GZ, RAR
- Future: Archive browsing

---

## 🔧 Backend Implementation

### Database Model

```python
class File(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_size = db.Column(db.Integer, nullable=False)
    mime_type = db.Column(db.String(100))
    file_hash = db.Column(db.String(64), index=True)
    category = db.Column(db.String(50), index=True)
    thumbnail_path = db.Column(db.String(500))
    description = db.Column(db.Text)
    extracted_text = db.Column(db.Text)
    uploaded_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'))
    is_public = db.Column(db.Boolean, default=False)
    download_count = db.Column(db.Integer, default=0)
    last_accessed = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
```

### API Endpoints

#### Upload Single File
```http
POST /api/files/upload
Authorization: Bearer {token}
Content-Type: multipart/form-data

file: (binary)
description: "Optional description"
task_id: 1 (optional)
is_public: false (optional)
```

**Response:**
```json
{
  "message": "File uploaded successfully",
  "file": {
    "id": 1,
    "filename": "document.pdf",
    "file_size": 1048576,
    "file_size_formatted": "1.0 MB",
    "category": "documents",
    "has_thumbnail": false,
    "has_extracted_text": true,
    "created_at": "2025-10-11T00:00:00"
  }
}
```

#### Bulk Upload
```http
POST /api/files/bulk-upload
Authorization: Bearer {token}
Content-Type: multipart/form-data

files: (multiple files)
```

**Response:**
```json
{
  "message": "Uploaded 3 files",
  "files": [...],
  "errors": []
}
```

#### List Files
```http
GET /api/files/list?category=images&search=report&page=1&per_page=20
Authorization: Bearer {token}
```

**Response:**
```json
{
  "files": [...],
  "total": 45,
  "page": 1,
  "per_page": 20,
  "pages": 3
}
```

#### Download File
```http
GET /api/files/download/{id}
Authorization: Bearer {token} (optional for public files)
```

Returns file with appropriate headers for download.

#### Preview File
```http
GET /api/files/preview/{id}
Authorization: Bearer {token} (optional for public files)
```

Returns file for inline display (images, PDFs).

#### Get Thumbnail
```http
GET /api/files/thumbnail/{id}
```

Returns PNG thumbnail for images.

#### AI Analysis
```http
POST /api/files/{id}/ai-analyze
Authorization: Bearer {token}
Content-Type: application/json

{
  "type": "summary"  // or "keywords", "sentiment", "questions"
}
```

**Response:**
```json
{
  "file_id": 1,
  "filename": "report.pdf",
  "analysis_type": "summary",
  "result": "This document discusses..."
}
```

#### Delete File
```http
DELETE /api/files/{id}
Authorization: Bearer {token}
```

---

## 🎨 Frontend Implementation

### FileManager Component

```jsx
import FileManager from './components/FileManager';

// Standalone usage
<FileManager />

// Task-specific files
<FileManager taskId={5} />

// With file selection callback
<FileManager onFileSelect={(file) => console.log(file)} />
```

### Features

**Drag-and-Drop Zone**
- Visual feedback on drag enter
- Multiple file drop support
- Automatic upload on drop

**Category Tabs**
- All Files
- Images
- Documents
- Spreadsheets
- Media
- Code
- Archives

**Search & Filter**
- Real-time search
- Category filtering
- Task filtering

**File Cards**
- Thumbnail preview (images)
- File icon (other types)
- File name and size
- Description
- Action buttons (Download, AI, Delete)
- Upload date

**AI Analysis**
- One-click AI analysis
- Loading indicator
- Results in modal
- Multiple analysis types

**Preview Modal**
- Full-size image preview
- PDF viewer
- Download fallback for unsupported types

---

## 🔒 Security Features

### File Validation
```python
ALLOWED_EXTENSIONS = {
    'images': {'png', 'jpg', 'jpeg', 'gif', 'webp', 'svg'},
    'documents': {'pdf', 'doc', 'docx', 'txt', 'md', 'rtf'},
    # ... more categories
}
```

### Size Limits
```python
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
```

### File Hashing
```python
def calculate_file_hash(file_path):
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()
```

### Access Control
- User-based ownership check
- Public/private flag
- Optional token authentication
- Task-based access (future)

---

## 🤖 AI Integration

### Text Extraction

**Supported Formats:**
- PDF (PyPDF2)
- Word documents (python-docx)
- Plain text files
- Code files
- Markdown

**Example:**
```python
def extract_text_from_file(file_path, file_type):
    if file_type == 'pdf':
        reader = PyPDF2.PdfReader(file_path)
        text = ''.join([page.extract_text() for page in reader.pages])
        return text[:10000]  # Limit to 10k chars
```

### AI Analysis Types

**Summary**
```
Prompt: "Summarize the following document in 3-5 sentences: {text}"
```

**Keywords**
```
Prompt: "Extract the top 10 keywords from this document: {text}"
```

**Sentiment**
```
Prompt: "Analyze the sentiment and tone of this document: {text}"
```

**Questions**
```
Prompt: "Generate 5 important questions that this document answers: {text}"
```

### AI API Integration
```python
import requests

ai_api_url = os.getenv('AI_API_URL', 'http://localhost:11434/api/generate')
ai_model = os.getenv('AI_MODEL', 'phi3')

response = requests.post(
    ai_api_url,
    json={'model': ai_model, 'prompt': prompt, 'stream': False},
    timeout=30
)
```

---

## 📁 File Storage Structure

```
uploads/
├── document_20251011_120000_1.pdf
├── image_20251011_120100_1.png
├── report_20251011_120200_2.docx
└── thumbnails/
    ├── thumb_image_20251011_120100_1.png.png
    └── thumb_photo_20251011_120300_1.jpg.png
```

### Filename Convention
```
{original_name}_{timestamp}_{user_id}.{extension}
```

---

## 🎯 Use Cases

### 1. Document Management
```
User uploads project documents
→ AI extracts text and generates summary
→ Files attached to specific tasks
→ Team members download and review
→ Track who accessed what
```

### 2. Image Gallery
```
User drags multiple images
→ Thumbnails generated automatically
→ Images displayed in grid
→ Click to preview full size
→ Download original files
```

### 3. AI Document Analysis
```
User uploads contract PDF
→ AI extracts key terms
→ AI generates summary
→ AI answers questions about content
→ User makes informed decisions
```

### 4. Code Repository
```
Developer uploads code files
→ Syntax preserved in text extraction
→ AI analyzes code structure
→ AI suggests improvements
→ Team reviews and downloads
```

---

## 🚀 Setup Instructions

### Backend Dependencies

```bash
pip install python-magic Pillow PyPDF2 python-docx
```

### Environment Variables

```env
UPLOAD_FOLDER=uploads
MAX_FILE_SIZE=52428800  # 50MB in bytes
```

### Create Upload Directory

```bash
mkdir -p uploads/thumbnails
chmod 755 uploads
```

### Database Migration

```python
from src.main import create_app, db
app = create_app()
with app.app_context():
    db.create_all()
```

---

## 🧪 Testing

### Upload Test
```bash
curl -X POST http://localhost:5000/api/files/upload \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@test.pdf" \
  -F "description=Test document" \
  -F "task_id=1"
```

### Bulk Upload Test
```bash
curl -X POST http://localhost:5000/api/files/bulk-upload \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "files=@file1.pdf" \
  -F "files=@file2.png" \
  -F "files=@file3.docx"
```

### AI Analysis Test
```bash
curl -X POST http://localhost:5000/api/files/1/ai-analyze \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"type": "summary"}'
```

---

## 📊 Performance Considerations

### Optimization Tips

1. **Thumbnail Generation**
   - Generate asynchronously
   - Use job queue for bulk uploads
   - Cache thumbnails

2. **Text Extraction**
   - Limit to first 10,000 characters
   - Extract on upload (not on-demand)
   - Store in database for quick access

3. **File Serving**
   - Use CDN for public files
   - Enable browser caching
   - Compress images

4. **Database Queries**
   - Index frequently queried fields
   - Use pagination
   - Eager load relationships

### Scalability

**Small Scale (< 1000 files)**
- Local file storage
- SQLite database
- Synchronous processing

**Medium Scale (1000-10000 files)**
- S3/Cloud storage
- PostgreSQL database
- Background job processing

**Large Scale (> 10000 files)**
- CDN integration
- Distributed storage
- Message queue for processing
- Elasticsearch for search

---

## 🐛 Troubleshooting

### Upload Fails

**Problem**: File upload returns 400 error  
**Solutions**:
- Check file size (must be under MAX_FILE_SIZE)
- Verify file type is allowed
- Ensure uploads/ directory exists and is writable
- Check disk space

### Thumbnail Not Generated

**Problem**: Image uploaded but no thumbnail  
**Solutions**:
- Verify Pillow is installed
- Check image file is valid
- Ensure thumbnails/ directory exists
- Check file permissions

### AI Analysis Fails

**Problem**: AI analysis returns error  
**Solutions**:
- Verify AI service is running (Ollama/LM Studio)
- Check AI_API_URL in .env
- Ensure file has extracted_text
- Verify network connectivity

### Preview Not Working

**Problem**: File preview shows error  
**Solutions**:
- Check MIME type is correct
- Verify browser supports file type
- Ensure file exists on disk
- Check CORS headers

---

## 🔮 Future Enhancements

- [ ] Video/audio player integration
- [ ] Archive file browsing (ZIP contents)
- [ ] Version control for files
- [ ] File sharing via links (like task sharing)
- [ ] Collaborative editing
- [ ] File comments and annotations
- [ ] Advanced search with filters
- [ ] File tagging system
- [ ] Automatic file categorization with AI
- [ ] OCR for scanned documents
- [ ] File conversion (PDF to Word, etc.)
- [ ] Virus scanning integration
- [ ] Duplicate file detection
- [ ] Storage quota management
- [ ] File expiration/auto-deletion

---

## 📝 Summary

The File Storage System provides a complete solution for managing files within Alex AI Workspace:

✅ **Easy Upload** - Drag-and-drop or click to upload  
✅ **Smart Organization** - Categories, search, and filters  
✅ **AI-Powered** - Automatic analysis and insights  
✅ **Secure** - Access control and validation  
✅ **Fast** - Thumbnails and caching  
✅ **Integrated** - Works with tasks and team collaboration  

**Perfect for**: Document management, image galleries, code repositories, project files, and any scenario requiring file storage with AI capabilities.

