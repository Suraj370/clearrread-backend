from fastapi import APIRouter
from models import DocumentRequest, RenameRequest
from document_service import DocumentService

router = APIRouter()
document_service = DocumentService()

@router.post("/create-document/")
async def create_document(request: DocumentRequest):
    """Create a new document."""
    return await document_service.create_document(request)

@router.post("/rename-document/")
async def rename_document(request: RenameRequest):
    """Rename an existing document."""
    return await document_service.rename_document(request)

@router.post("/convert-text/")
async def convert_text(request: DocumentRequest):
    """Convert text to dyslexia-friendly format."""
    return await document_service.convert_text(request)