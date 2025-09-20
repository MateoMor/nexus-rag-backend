from pydantic import BaseModel, Field
from typing import Optional, List

class ChatRequest(BaseModel):
    message: str = Field(..., description="User message")
    conversation_id: Optional[str] = Field(None, description="Conversation ID")
    
class DocumentUploadRequest(BaseModel):
    filename: str = Field(..., description="Document filename")
    content_type: str = Field(..., description="Document content type")

class DocumentDeleteRequest(BaseModel):
    document_id: str = Field(..., description="Document ID to delete")