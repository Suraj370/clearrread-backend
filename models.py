from pydantic import BaseModel
from google.cloud.firestore_v1 import DocumentReference

class DocumentRequest(BaseModel):
    userId: str
    name: str | None = None
    originalText: str | None = None

class RenameRequest(BaseModel):
    userId: str
    docId: str
    oldName: str
    newName: str

def firestore_to_json(data: dict) -> dict:
    """Convert Firestore document data to JSON-serializable format."""
    result = {}
    for key, value in data.items():
        if isinstance(value, DocumentReference):
            result[key] = value.id
        else:
            result[key] = value
    return result