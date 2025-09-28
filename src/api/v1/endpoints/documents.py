from typing import List

from fastapi import APIRouter, File, HTTPException, UploadFile

from src.models.responses import DocumentInfo, DocumentListResponse, DocumentUploadResponse
from src.services.object_storage import ObjectStorageError, get_object_storage_service

import uuid

router = APIRouter()


def _document_prefix(document_id: str) -> str:
    return f"documents/{document_id}"

@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(file: UploadFile = File(...)):
    """Upload a document for RAG processing"""
    try:
        storage_service = get_object_storage_service()

        # Generate unique document ID
        document_id = str(uuid.uuid4())
        prefix = _document_prefix(document_id)

        storage_key = storage_service.build_key(file.filename or "file", prefix=prefix)
        upload_result = await storage_service.upload_file(
            file,
            destination_path=storage_key,
            metadata={"document_id": document_id},
        )

        # TODO: Process document with LlamaIndex usando el archivo en R2

        return DocumentUploadResponse(
            message="Document uploaded successfully",
            document_id=document_id,
            filename=file.filename,
            url=upload_result.url,
        )
    except ObjectStorageError as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

@router.get("/", response_model=DocumentListResponse)
async def list_documents():
    """List all uploaded documents"""
    try:
        storage_service = get_object_storage_service()
        objects = await storage_service.list_objects(prefix="documents", max_keys=1000)

        documents: List[DocumentInfo] = []
        for obj in objects:
            parts = obj.key.split("/")
            if len(parts) < 3:
                # Skip objects that do not follow the documents/<id>/<filename> structure
                continue

            _, document_id, *filename_parts = parts
            filename = "/".join(filename_parts) if filename_parts else obj.filename

            documents.append(
                DocumentInfo(
                    id=document_id,
                    filename=filename,
                    url=obj.url,
                    size=obj.size,
                    last_modified=obj.last_modified,
                )
            )

        documents.sort(
            key=lambda doc: doc.last_modified.timestamp() if doc.last_modified else float("-inf"),
            reverse=True,
        )

        return DocumentListResponse(documents=documents, total=len(documents))
    except ObjectStorageError as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

@router.delete("/{document_id}")
async def delete_document(document_id: str):
    """Delete a document"""
    try:
        storage_service = get_object_storage_service()

        prefix = _document_prefix(document_id)
        deleted_count = await storage_service.delete_prefix(prefix)

        if deleted_count == 0:
            raise HTTPException(status_code=404, detail="Document not found")

        return {"message": "Document deleted successfully"}
    except ObjectStorageError as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))