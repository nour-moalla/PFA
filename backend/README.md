# UtopiaHire Career Services - Unified Backend API

A comprehensive FastAPI backend that combines features from 4 career service applications:
- **Resume Analysis & ATS Scoring** (from CV Reviewer)
- **AI-Powered Interviews** (from AI Interviewer)
- **Career Insights & Roadmaps** (from Career Insight Report)
- **Job Matching** (from Job Matcher)

## Features

### 🎯 Resume Analysis
- Upload and parse resumes/CVs (PDF support)
- ATS (Applicant Tracking System) scoring (0-100)
- Detailed feedback and improvement suggestions
- Skill extraction and matching
- Structured data extraction (contact info, experience, education, etc.)

### 🤖 AI Interview
- Conduct AI-powered technical interviews
- Code question support with syntax highlighting markers
- Real-time scoring and feedback
- Interview history tracking
- Multiple question types (technical, behavioral, coding, system design)

### 📊 Career Insights
- Market skill analysis
- Personalized learning roadmaps (Markdown + PDF export)
- Skill gap identification
- Skill clustering and visualization
- Career progression recommendations

### 🔍 Job Matching
- Semantic job matching using embeddings
- CV-to-job similarity scoring
- Top job recommendations
- Job database search

## Tech Stack

- **Framework**: FastAPI
- **AI/LLM**: OpenAI-compatible API (supports NVIDIA NIM, OpenAI, etc.)
- **Embeddings**: Sentence Transformers (all-MiniLM-L6-v2)
- **PDF Processing**: pdfplumber, pypdf
- **Data Processing**: pandas, numpy
- **ML**: scikit-learn, hdbscan

## Installation

### Prerequisites
- Python 3.9+
- pip

### Setup

1. **Clone and navigate to backend directory:**
```bash
cd backend
```

2. **Create virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Create `.env` file:**
```bash
# AI Service Configuration
AI_API_KEY=your_api_key_here
AI_BASE_URL=https://integrate.api.nvidia.com/v1  # or your OpenAI-compatible endpoint
AI_MODEL=meta/llama-3.1-405b-instruct  # or your preferred model

# Optional: Override defaults
# EMBEDDING_MODEL_NAME=all-MiniLM-L6-v2
# UPLOAD_FOLDER=uploads
# DEMANDED_SKILLS_CSV_PATH=data/skill_summary_ranked.csv
# JOBS_DATABASE_PATH=data/jobs_database.csv
```

5. **Create necessary directories:**
```bash
mkdir -p uploads static data
```

6. **Add data files (optional):**
   - Place `skill_summary_ranked.csv` in `data/` for career insights
   - Place `jobs_database.csv` in `data/` for job matching

## Running the Server

### Development
```bash
python main.py
```

Or using uvicorn directly:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Production
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

The API will be available at:
- **API**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API Documentation

### Health Check
```bash
GET /health
```

### Resume Analysis

#### Upload and Parse Resume
```bash
POST /api/resume/upload
Content-Type: multipart/form-data

file: <PDF file>
job_description: (optional)
job_title: (optional)
company: (optional)
experience: (optional)
```

#### Analyze Resume with ATS Scoring
```bash
POST /api/resume/analyze
Content-Type: multipart/form-data

file: <PDF file>
job_description: (optional)
job_title: (optional)
company: (optional)
experience: (optional)
```

#### Extract Skills
```bash
POST /api/resume/extract-skills
Content-Type: multipart/form-data

file: <PDF file>
```

### AI Interview

#### Start Interview
```bash
POST /api/interview/start
Content-Type: application/json

{
  "cv_text": "resume text here",
  "role": "Software Engineer"
}
```

#### Submit Answer
```bash
POST /api/interview/answer
Content-Type: application/json

{
  "session_id": "uuid",
  "answer": "candidate answer",
  "is_code": false
}
```

#### Get Interview History
```bash
GET /api/interview/history/{session_id}
```

#### Get Scores
```bash
GET /api/interview/scores/{session_id}
```

#### Request Code Question
```bash
POST /api/interview/code-question/{session_id}
```

### Career Insights

#### Get Market Insights
```bash
GET /api/career/market-insights
```

#### Upload CV for Analysis
```bash
POST /api/career/upload-cv
Content-Type: multipart/form-data

file: <PDF or TXT file>
```

#### Analyze Skills
```bash
POST /api/career/analyze
Content-Type: application/json

{
  "skills": ["Python", "JavaScript", "React"]
}
```

#### Cluster Skills
```bash
POST /api/career/cluster-skills
Content-Type: application/json

{
  "skills": ["Python", "Django", "Flask", "React", "Vue"]
}
```

### Job Matching

#### Match CV to Jobs
```bash
POST /api/jobs/match-cv
Content-Type: multipart/form-data

file: <PDF file>
```

#### Get Database Info
```bash
GET /api/jobs/database-info
```

## Project Structure

```
backend/
├── main.py                 # FastAPI application entry point
├── requirements.txt        # Python dependencies
├── README.md              # This file
├── .env                   # Environment variables (create this)
├── app/
│   ├── __init__.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py      # Configuration settings
│   │   ├── ai_service.py  # Unified AI service
│   │   └── resume_parser.py # Resume parsing logic
│   └── routers/
│       ├── __init__.py
│       ├── resume.py      # Resume analysis endpoints
│       ├── interview.py   # AI interview endpoints
│       ├── career_insights.py # Career insights endpoints
│       └── job_matching.py # Job matching endpoints
├── uploads/               # Temporary file uploads
├── static/                # Generated files (PDFs, etc.)
└── data/                  # Data files (CSVs, etc.)
```

## Configuration

All configuration is managed through environment variables and `app/core/config.py`. Key settings:

- `AI_API_KEY`: Your AI/LLM API key
- `AI_BASE_URL`: Base URL for OpenAI-compatible API
- `AI_MODEL`: Model name to use
- `CORS_ORIGINS`: Allowed CORS origins
- `UPLOAD_FOLDER`: Directory for file uploads
- `MAX_FILE_SIZE`: Maximum file size (default: 16MB)

## Unified AI Model

This backend uses a **single unified AI model** for all LLM operations:
- Resume analysis and ATS scoring
- Interview question generation
- Skill extraction
- Roadmap generation
- CV data extraction

The AI service is configured to work with any OpenAI-compatible API, including:
- NVIDIA NIM
- OpenAI
- Other compatible providers

## Error Handling

All endpoints include comprehensive error handling:
- File validation
- API error retries with exponential backoff
- Graceful degradation when data files are missing
- Clear error messages

## Development

### Adding New Features

1. Create new router in `app/routers/`
2. Add endpoints with proper documentation
3. Use `ai_service` for LLM operations
4. Update `main.py` to include the router

### Testing

```bash
# Test health endpoint
curl http://localhost:8000/health

# Test resume upload
curl -X POST http://localhost:8000/api/resume/upload \
  -F "file=@resume.pdf"
```

## License

This project is part of the UtopiaHire Career Services suite.

## Support

For issues or questions, please refer to the main project documentation.

