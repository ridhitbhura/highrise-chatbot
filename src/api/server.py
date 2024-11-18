from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from src.main.simple_faq_chatbot import SimpleFAQChatbot
from datetime import datetime

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Add your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize chatbot
chatbot = SimpleFAQChatbot('data/highrise_faq.json')

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
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/feedback")
async def feedback(request: FeedbackRequest):
    try:
        # Add logging to debug
        print(f"Received feedback: {request}")
        
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
        print(f"Feedback error: {str(e)}")  # Add debug logging
        raise HTTPException(status_code=500, detail=str(e)) 