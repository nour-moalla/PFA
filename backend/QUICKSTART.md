# Quick Start Guide

## 1. Setup Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## 2. Configure Environment Variables

Create a `.env` file in the `backend` directory:

```env
AI_API_KEY=your_api_key_here
AI_BASE_URL=https://integrate.api.nvidia.com/v1
AI_MODEL=meta/llama-3.1-405b-instruct
```

## 3. Create Required Directories

```bash
mkdir -p uploads static data
```

## 4. Run the Server

```bash
python main.py
```

Or with uvicorn:

```bash
uvicorn main:app --reload
```

## 5. Access the API

- **API Base**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 6. Test the API

### Health Check
```bash
curl http://localhost:8000/health
```

### Upload and Analyze Resume
```bash
curl -X POST "http://localhost:8000/api/resume/analyze" \
  -F "file=@your_resume.pdf" \
  -F "job_title=Software Engineer" \
  -F "company=Tech Corp"
```

## Features Available

### Resume Analysis (`/api/resume`)
- `POST /api/resume/upload` - Upload and parse resume
- `POST /api/resume/analyze` - Full ATS analysis
- `POST /api/resume/extract-skills` - Extract skills only

### AI Interview (`/api/interview`)
- `POST /api/interview/start` - Start interview session
- `POST /api/interview/answer` - Submit answer
- `GET /api/interview/history/{session_id}` - Get history
- `GET /api/interview/scores/{session_id}` - Get scores

### Career Insights (`/api/career`)
- `GET /api/career/market-insights` - Get market trends
- `POST /api/career/upload-cv` - Upload CV for analysis
- `POST /api/career/analyze` - Analyze skills and generate roadmap
- `POST /api/career/cluster-skills` - Cluster skills

### Job Matching (`/api/jobs`)
- `POST /api/jobs/match-cv` - Match CV to jobs
- `GET /api/jobs/database-info` - Get database info

## Next Steps

1. Add your data files to `data/` directory:
   - `skill_summary_ranked.csv` for career insights
   - `jobs_database.csv` for job matching

2. Explore the interactive API documentation at `/docs`

3. Integrate with your frontend applications

