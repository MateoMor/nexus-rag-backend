from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class ChatResponse(BaseModel):
    response: str = Field(..., description="AI response")
    conversation_id: str = Field(..., description="Conversation ID")
    timestamp: datetime = Field(..., description="Response timestamp")
    sources: Optional[List[str]] = Field(None, description="Source documents")

class DocumentInfo(BaseModel):
    id: str = Field(..., description="Document identifier")
    filename: str = Field(..., description="Original filename")
    url: Optional[str] = Field(None, description="Public URL for the stored document")
    size: Optional[int] = Field(None, description="Document size in bytes")
    last_modified: Optional[datetime] = Field(None, description="Last modification timestamp in storage")


class DocumentUploadResponse(BaseModel):
    message: str = Field(..., description="Upload status message")
    document_id: str = Field(..., description="Generated document ID")
    filename: str = Field(..., description="Original filename")
    url: Optional[str] = Field(None, description="Public URL for the uploaded document")

class HealthResponse(BaseModel):
    status: str = Field(..., description="Service status")
    timestamp: datetime = Field(..., description="Check timestamp")
    version: str = Field(..., description="API version")

class DocumentListResponse(BaseModel):
    documents: List[DocumentInfo] = Field(..., description="List of documents")
    total: int = Field(..., description="Total number of documents")