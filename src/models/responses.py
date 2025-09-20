from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class ChatResponse(BaseModel):
    response: str = Field(..., description="AI response")
    conversation_id: str = Field(..., description="Conversation ID")
    timestamp: datetime = Field(..., description="Response timestamp")
    sources: Optional[List[str]] = Field(None, description="Source documents")

class DocumentUploadResponse(BaseModel):
    message: str = Field(..., description="Upload status message")
    document_id: str = Field(..., description="Generated document ID")
    filename: str = Field(..., description="Original filename")

class HealthResponse(BaseModel):
    status: str = Field(..., description="Service status")
    timestamp: datetime = Field(..., description="Check timestamp")
    version: str = Field(..., description="API version")

class DocumentListResponse(BaseModel):
    documents: List[dict] = Field(..., description="List of documents")
    total: int = Field(..., description="Total number of documents")