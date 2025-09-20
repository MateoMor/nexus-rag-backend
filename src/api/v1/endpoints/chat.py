from fastapi import APIRouter, HTTPException
from src.models.requests import ChatRequest
from src.models.responses import ChatResponse
from datetime import datetime
import uuid

router = APIRouter()

@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Chat endpoint for RAG conversations"""
    try:
        # Generate conversation ID if not provided
        conversation_id = request.conversation_id or str(uuid.uuid4())
        
        # For now, return a mock response
        # TODO: Implement actual RAG service integration
        response_text = f"Echo: {request.message}"
        
        return ChatResponse(
            response=response_text,
            conversation_id=conversation_id,
            timestamp=datetime.now(),
            sources=["mock_document.pdf"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))