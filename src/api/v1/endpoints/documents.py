from fastapi import APIRouter, UploadFile, File, HTTPException
from src.models.responses import DocumentUploadResponse, DocumentListResponse
from typing import List
import uuid
import os

router = APIRouter()

@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(file: UploadFile = File(...)):
    """Upload a document for RAG processing"""
    try:
        # Generate unique document ID
        document_id = str(uuid.uuid4())
        
        # Create documents directory if it doesn't exist
        os.makedirs("data/documents", exist_ok=True)
        
        # Save file
        file_path = f"data/documents/{document_id}_{file.filename}"
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # TODO: Process document with LlamaIndex
        
        return DocumentUploadResponse(
            message="Document uploaded successfully",
            document_id=document_id,
            filename=file.filename
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=DocumentListResponse)
async def list_documents():
    """List all uploaded documents"""
    try:
        documents_dir = "data/documents"
        if not os.path.exists(documents_dir):
            return DocumentListResponse(documents=[], total=0)
        
        files = os.listdir(documents_dir)
        documents = [{"filename": f, "id": f.split("_")[0]} for f in files]
        
        return DocumentListResponse(
            documents=documents,
            total=len(documents)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{document_id}")
async def delete_document(document_id: str):
    """Delete a document"""
    try:
        documents_dir = "data/documents"
        files = [f for f in os.listdir(documents_dir) if f.startswith(document_id)]
        
        if not files:
            raise HTTPException(status_code=404, detail="Document not found")
        
        for file in files:
            os.remove(os.path.join(documents_dir, file))
        
        return {"message": "Document deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))