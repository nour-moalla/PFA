"""
AI Interview Router
Handles AI-powered interview sessions
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Annotated
from datetime import datetime
import uuid

from app.core.ai_service import ai_service
from app.core.resume_parser import ResumeParser
from app.core.config import settings
from app.core.auth import AuthUser, get_current_user

router = APIRouter()

# Store active interview sessions
interview_sessions: Dict[str, Dict] = {}

# Initialize resume parser
resume_parser = ResumeParser()


def _get_owned_session(session_id: str, user_uid: str) -> Dict:
    """Return interview session if it belongs to the authenticated user."""
    if session_id not in interview_sessions:
        raise HTTPException(status_code=404, detail="Invalid session ID")

    session = interview_sessions[session_id]
    if session.get("owner_uid") != user_uid:
        raise HTTPException(status_code=403, detail="You are not allowed to access this session")
    return session


class InterviewStartRequest(BaseModel):
    """Request to start an interview"""
    cv_text: Optional[str] = None
    cv_file_id: Optional[str] = None
    role: str = "Software Engineer"


class InterviewAnswerRequest(BaseModel):
    """Request to submit an interview answer"""
    session_id: str
    answer: str
    is_code: bool = False


class Interviewer:
    """Manages interview session state and logic"""
    
    def __init__(self, role: str, cv_summary: str):
        self.role = role
        self.cv_summary = cv_summary
        self.question_count = 0
        self.history: List[Dict[str, str]] = []
        self.scores = {
            "technical_knowledge": 0,
            "communication": 0,
            "problem_solving": 0,
            "relevance": 0
        }
        self.is_finished = False
        self.max_questions = settings.MAX_QUESTIONS
    
    def ask_first_question(self) -> str:
        """Generate the first interview question"""
        system_prompt = f"""You are a professional technical interviewer conducting an interview for a {self.role} position.
Your goal is to assess the candidate's technical knowledge, problem-solving abilities, and communication skills.
Ask relevant, challenging questions appropriate for this role."""
        
        user_prompt = f"""
You are interviewing a candidate for a {self.role} position.

Candidate's Resume Summary:
{self.cv_summary}

Ask the first interview question. Make it relevant to the role and the candidate's background.
Be professional and engaging. This is question 1 of approximately {self.max_questions} questions.
"""
        
        question = ai_service.chat_completion(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=0.7,
            max_tokens=500
        )
        
        self.question_count = 1
        self.history.append({
            "role": "interviewer",
            "content": question,
            "timestamp": datetime.now().isoformat()
        })
        
        return question
    
    def respond_to_candidate(self, answer: str, is_code: bool = False) -> str:
        """Process candidate answer and generate next question or feedback"""
        if self.is_finished:
            return "Interview has already concluded. Thank you for your participation!"
        
        # Add candidate answer to history
        self.history.append({
            "role": "candidate",
            "content": answer,
            "is_code": is_code,
            "timestamp": datetime.now().isoformat()
        })
        
        # Build context from history
        history_context = "\n".join([
            f"{msg['role'].upper()}: {msg['content'][:500]}"
            for msg in self.history[-5:]  # Last 5 messages for context
        ])
        
        if is_code:
            system_prompt = f"""You are a technical interviewer reviewing code submissions for a {self.role} position.
Provide detailed feedback on:
- Code correctness and logic
- Code quality and best practices
- Performance considerations
- Edge case handling
- Suggestions for improvement"""
            
            user_prompt = f"""
Review this code submission from the candidate:

{answer}

Provide comprehensive feedback. Then ask the next interview question if appropriate.
This is question {self.question_count} of approximately {self.max_questions}.
"""
        else:
            system_prompt = f"""You are a professional technical interviewer conducting an interview for a {self.role} position.
Assess the candidate's answers and ask follow-up questions or move to the next topic."""
            
            user_prompt = f"""
Interview Context:
{history_context}

The candidate just answered your question. Provide brief feedback on their answer, then ask the next question.
This is question {self.question_count} of approximately {self.max_questions}.
Make sure to vary question types (technical, behavioral, coding, system design, etc.) based on the role.
"""
        
        response = ai_service.chat_completion(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=0.7,
            max_tokens=800
        )
        
        self.question_count += 1
        self.history.append({
            "role": "interviewer",
            "content": response,
            "timestamp": datetime.now().isoformat()
        })
        
        # Check if interview should end
        if self.question_count >= self.max_questions:
            self.is_finished = True
            # Add closing message
            closing = "\n\nThank you for participating in this interview. We will review your responses and get back to you soon."
            response += closing
        
        return response
    
    def request_code_question(self) -> str:
        """Request AI to provide a properly formatted code question"""
        system_prompt = f"""You are a technical interviewer for a {self.role} position.
Create coding questions with proper formatting markers."""
        
        user_prompt = f"""
Please provide a coding question now. Use EXACTLY this format:

[CODE_QUESTION]
[Your problem description here]
[LANGUAGE] python [/LANGUAGE]
[STARTER_CODE]
def solution():
    # starter code
    pass
[/STARTER_CODE]

Make sure to include all the markers. The question should be appropriate for a {self.role} role.
"""
        
        response = ai_service.chat_completion(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=0.7,
            max_tokens=600
        )
        
        self.history.append({
            "role": "interviewer",
            "content": response,
            "timestamp": datetime.now().isoformat()
        })
        
        return response
    
    def get_scores(self) -> Dict:
        """Calculate and return interview scores"""
        # Simple scoring based on question count and interview completion
        # In a real implementation, this would analyze the answers more deeply
        base_score = min(100, (self.question_count / self.max_questions) * 100)
        
        return {
            "technical_knowledge": int(base_score * 0.3),
            "communication": int(base_score * 0.25),
            "problem_solving": int(base_score * 0.25),
            "relevance": int(base_score * 0.2),
            "overall": int(base_score)
        }
    
    def get_history(self) -> List[Dict[str, str]]:
        """Get interview history"""
        return self.history


@router.post("/start")
async def start_interview(
    request: InterviewStartRequest,
    current_user: Annotated[AuthUser, Depends(get_current_user)],
):
    """
    Start a new interview session
    
    - **cv_text**: Resume text (optional if cv_file_id provided)
    - **cv_file_id**: ID of previously uploaded CV (optional if cv_text provided)
    - **role**: Job role for the interview
    """
    # Get CV summary
    if request.cv_text:
        cv_summary = ai_service.summarize_resume(request.cv_text)
    elif request.cv_file_id:
        # In a real implementation, retrieve CV from storage
        raise HTTPException(status_code=400, detail="CV file retrieval not yet implemented. Please provide cv_text.")
    else:
        raise HTTPException(status_code=400, detail="Either cv_text or cv_file_id must be provided")
    
    # Create interview session
    session_id = str(uuid.uuid4())
    interviewer = Interviewer(role=request.role, cv_summary=cv_summary)
    
    # Get first question
    first_question = interviewer.ask_first_question()
    
    # Store session
    interview_sessions[session_id] = {
        'interviewer': interviewer,
        'cv_summary': cv_summary,
        'role': request.role,
        'created_at': datetime.now().isoformat(),
        'owner_uid': current_user.uid,
    }
    
    return {
        "session_id": session_id,
        "cv_summary": cv_summary,
        "first_question": first_question,
        "role": request.role,
        "is_finished": False,
        "question_count": 1
    }


@router.post("/answer")
async def submit_answer(
    request: InterviewAnswerRequest,
    current_user: Annotated[AuthUser, Depends(get_current_user)],
):
    """
    Submit an answer and get the next question or feedback
    
    - **session_id**: Interview session ID
    - **answer**: Candidate's answer
    - **is_code**: Whether the answer is code
    """
    session = _get_owned_session(request.session_id, current_user.uid)
    interviewer = session['interviewer']
    
    if interviewer.is_finished:
        return {
            "response": "Interview has already concluded.",
            "is_finished": True,
            "question_count": interviewer.question_count,
            "scores": interviewer.get_scores()
        }
    
    # Get AI response
    ai_response = interviewer.respond_to_candidate(request.answer, is_code=request.is_code)
    
    # Get scores
    scores_data = interviewer.get_scores()
    
    return {
        "response": ai_response,
        "is_finished": interviewer.is_finished,
        "question_count": interviewer.question_count,
        "scores": scores_data
    }


@router.get("/history/{session_id}")
async def get_history(
    session_id: str,
    current_user: Annotated[AuthUser, Depends(get_current_user)],
):
    """Get interview history for a session"""
    session = _get_owned_session(session_id, current_user.uid)
    interviewer = session['interviewer']
    history = interviewer.get_history()
    
    return {
        "history": history,
        "question_count": interviewer.question_count,
        "is_finished": interviewer.is_finished
    }


@router.get("/scores/{session_id}")
async def get_scores(
    session_id: str,
    current_user: Annotated[AuthUser, Depends(get_current_user)],
):
    """Get interview scores for a session"""
    session = _get_owned_session(session_id, current_user.uid)
    interviewer = session['interviewer']
    scores_data = interviewer.get_scores()
    
    return {
        "scores": scores_data,
        "is_finished": interviewer.is_finished
    }


@router.post("/code-question/{session_id}")
async def request_code_question(
    session_id: str,
    current_user: Annotated[AuthUser, Depends(get_current_user)],
):
    """Request AI to provide a properly formatted code question"""
    session = _get_owned_session(session_id, current_user.uid)
    interviewer = session['interviewer']
    
    response = interviewer.request_code_question()
    
    return {
        "response": response,
        "is_finished": interviewer.is_finished
    }


@router.delete("/session/{session_id}")
async def end_session(
    session_id: str,
    current_user: Annotated[AuthUser, Depends(get_current_user)],
):
    """End interview session and cleanup"""
    _get_owned_session(session_id, current_user.uid)
    if session_id in interview_sessions:
        del interview_sessions[session_id]
        return {"message": "Session ended successfully"}
    else:
        raise HTTPException(status_code=404, detail="Session not found")

