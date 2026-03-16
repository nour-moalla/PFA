# Herotopia Career Services - Unified React Frontend

A comprehensive career development platform combining all features from the original apps into a single, unified React application.

## Authentication

The app uses Firebase Authentication with the following features:

- **Email/Password Authentication** - Traditional sign up and sign in
- **Google Sign-In** - One-click authentication with Google account
- **Passwordless Sign-In** - Sign in via email link (no password required)
- **Protected Routes** - All feature pages require authentication
- **User Profile** - Display user info in navigation with logout option

### Authentication Pages

- `/login` - Sign in page with email/password, Google, and email link options
- `/signup` - Sign up page with full registration process
- `/forgot-password` - Password reset via email

### Protected Routes

The following routes require authentication:
- `/resume` - Resume Analysis
- `/interview` - AI Interview
- `/career` - Career Insights
- `/jobs` - Job Matching

Unauthenticated users will be redirected to the login page.

## Features

### 1. Resume Analysis
- Upload and parse resumes/CVs
- ATS (Applicant Tracking System) scoring
- Detailed feedback and improvement suggestions
- Skill extraction and matching

### 2. AI Interview
- Conduct AI-powered interviews
- Code question support with syntax highlighting
- Real-time scoring and feedback
- Interview history tracking

### 3. Career Insights
- Market skill analysis
- Personalized learning roadmaps
- Skill gap identification
- Career progression recommendations

### 4. Job Matching
- Semantic job matching using embeddings
- CV-to-job similarity scoring
- Top job recommendations
- Job database search

## Tech Stack

- **React 18** - UI framework
- **React Router** - Client-side routing
- **Vite** - Build tool and dev server
- **Tailwind CSS** - Styling
- **Axios** - HTTP client
- **Firebase Authentication** - User authentication and authorization

## Getting Started

### Prerequisites

- Node.js 18+ and npm/yarn
- Backend API running on `http://localhost:8000` (see `../backend/README.md`)
- Firebase project with Authentication enabled

### Firebase Setup

1. **Create a Firebase Project:**
   - Go to [Firebase Console](https://console.firebase.google.com/)
   - Create a new project or select an existing one

2. **Enable Authentication:**
   - Go to Authentication > Sign-in method
   - Enable **Email/Password** authentication
   - Enable **Google** authentication (optional but recommended)
   - Enable **Email link (passwordless sign-in)** authentication

3. **Get Firebase Configuration:**
   - Go to Project Settings > General
   - Scroll down to "Your apps" section
   - Click on the Web app icon (`</>`) or add a new web app
   - Copy the Firebase configuration values

4. **Create `.env` file:**
   ```bash
   cp .env.example .env
   ```
   
   Fill in your Firebase credentials:
   ```env
   VITE_FIREBASE_API_KEY=your_api_key_here
   VITE_FIREBASE_AUTH_DOMAIN=your-project-id.firebaseapp.com
   VITE_FIREBASE_PROJECT_ID=your-project-id
   VITE_FIREBASE_STORAGE_BUCKET=your-project-id.appspot.com
   VITE_FIREBASE_MESSAGING_SENDER_ID=your_messaging_sender_id
   VITE_FIREBASE_APP_ID=your_app_id
   ```

5. **Configure Authorized Domains:**
   - In Firebase Console, go to Authentication > Settings > Authorized domains
   - Add `localhost` if not already present
   - Add your production domain when deploying

### Installation

```bash
cd frontend
npm install
```

### Development

```bash
npm run dev
```

The app will be available at `http://localhost:5173`

### Build for Production

```bash
npm run build
```

The built files will be in the `dist` directory.

### Preview Production Build

```bash
npm run preview
```

## Project Structure

```
frontend/
├── src/
│   ├── api/
│   │   └── client.js          # API client with all endpoints
│   ├── components/
│   │   ├── Layout.jsx         # Main layout with navigation
│   │   └── CodeEditor.jsx     # Code editor for interviews
│   ├── pages/
│   │   ├── HomePage.jsx      # Homepage with feature overview
│   │   ├── ResumeAnalysis.jsx # Resume analysis page
│   │   ├── AIInterview.jsx    # AI interview page
│   │   ├── CareerInsights.jsx # Career insights page
│   │   └── JobMatching.jsx    # Job matching page
│   ├── App.jsx                # Main app component with routing
│   ├── main.jsx               # Entry point
│   └── index.css              # Global styles
├── index.html
├── package.json
├── vite.config.js
└── tailwind.config.js
```

## API Integration

The app connects to the unified backend API at `http://localhost:8000`. All API endpoints are defined in `src/api/client.js`:

- **Resume API**: `/api/resume/*`
- **Interview API**: `/api/interview/*`
- **Career API**: `/api/career/*`
- **Job API**: `/api/jobs/*`

## Environment Variables

Create a `.env` file in the `frontend` directory:

```env
VITE_API_URL=http://localhost:8000
```

## Styling

The app uses Tailwind CSS with a design system matching the original Vue app:
- Clean, modern UI
- Responsive design
- Blue color scheme for primary actions
- Consistent spacing and typography

## Features from Original Apps

### From Vue Frontend (`/frontend`)
- Clean navigation bar
- Consistent styling and layout
- User-friendly file upload interface

### From AI Interviewer (`/AI Interviewer/frontend`)
- Chat-based interview interface
- Code editor with syntax highlighting
- Real-time scoring display

### From CV Reviewer (`/CV Reviewer/frontend`)
- Comprehensive resume analysis
- ATS scoring with detailed breakdown
- Pros/cons and improvement suggestions

### From Career Insight Report (`/Career insight report`)
- Market insights sidebar
- Two-column layout
- Roadmap generation and PDF download

### From Job Matcher (`/Job Matcher`)
- Semantic job matching
- Similarity scoring
- Job recommendations

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## License

Part of the Herotopia Career Services suite.

