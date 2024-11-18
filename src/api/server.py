from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from src.main.simple_faq_chatbot import SimpleFAQChatbot
from datetime import datetime
import uuid
import os

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://your-frontend-domain.vercel.app"  # Add your Vercel domain
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Get the absolute path to the data directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FAQ_PATH = os.path.join(BASE_DIR, 'data', 'highrise_faq.json')

# Initialize chatbot with absolute path
chatbot = SimpleFAQChatbot(FAQ_PATH)

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None

class FeedbackRequest(BaseModel):
    message_id: str
    session_id: str
    is_helpful: bool
    comments: Optional[str] = None

@app.post("/api/chat")
async def chat(request: ChatRequest):
    try:
        response = await chatbot.handle_message(request.message, request.session_id)
        return {
            **response,
            "message_id": str(uuid.uuid4())  # Add unique message ID
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/feedback")
async def feedback(request: FeedbackRequest):
    try:
        success = await chatbot.store_feedback({
            "messageId": request.message_id,
            "sessionId": request.session_id,
            "isHelpful": request.is_helpful,
            "comments": request.comments,
            "timestamp": datetime.now().isoformat()
        })
        
        if success:
            return {"message": "Feedback stored successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to store feedback")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy"} 