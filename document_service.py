import logging
from firebase_admin import firestore
from fastapi import HTTPException
from database import get_firestore_client
from models import DocumentRequest, RenameRequest, firestore_to_json
from text_converter import dyslexia_friendly_convert

logger = logging.getLogger(__name__)

class DocumentService:
    def __init__(self):
        self.db = get_firestore_client()

    async def create_document(self, request: DocumentRequest):
        """Create a new document for a user."""
        try:
            documents_ref = self.db.collection("documents")
            snapshot = documents_ref.where("userId", "==", request.userId).get()
            existing_names = [doc.to_dict()["name"] for doc in snapshot]

            n = 1
            new_name = f"Untitled Document {n}"
            while new_name in existing_names:
                n += 1
                new_name = f"Untitled Document {n}"

            doc_ref = documents_ref.document()
            doc_data = {
                "name": new_name,
                "originalText": "",
                "convertedText": "",
                "userId": request.userId,
                "timestamp": firestore.SERVER_TIMESTAMP
            }
            doc_ref.set(doc_data)

            created_doc = doc_ref.get()
            if not created_doc.exists:
                raise ValueError("Failed to retrieve created document")

            doc_dict = created_doc.to_dict()
            doc_dict["id"] = created_doc.id
            json_compatible_data = firestore_to_json(doc_dict)

            logger.info(f"Created document {doc_ref.id} for user {request.userId}")
            return json_compatible_data
            
        except Exception as e:
            logger.error(f"Error creating document: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail=str(e))

    async def rename_document(self, request: RenameRequest):
        """Rename an existing document."""
        try:
            documents_ref = self.db.collection("documents")
            snapshot = documents_ref.where("userId", "==", request.userId).get()
            existing_names = [doc.to_dict()["name"] for doc in snapshot]

            final_name = request.newName
            if final_name in existing_names:
                k = 2
                while f"{final_name} ({k})" in existing_names:
                    k += 1
                final_name = f"{final_name} ({k})"

            doc_ref = documents_ref.document(request.docId)
            doc = doc_ref.get()
            if not doc.exists or doc.to_dict()["name"] != request.oldName:
                raise HTTPException(status_code=404, detail="Document not found")

            doc_ref.update({"name": final_name})
            logger.info(f"Renamed document {request.docId} to {final_name}")
            return {"docId": request.docId, "newName": final_name}
            
        except Exception as e:
            logger.error(f"Error renaming document: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    async def convert_text(self, request: DocumentRequest):
        """Convert text to dyslexia-friendly format and update document."""
        try:
            if not request.originalText:
                raise HTTPException(status_code=400, detail="Original text is required")

            logger.info(f"Received text for conversion: {request.originalText}")
            converted_text = dyslexia_friendly_convert(request.originalText)
            logger.info(f"Converted text: {converted_text}")

            documents_ref = self.db.collection("documents")
            snapshot = documents_ref.where("userId", "==", request.userId).get()
            
            for doc in snapshot:
                if doc.to_dict().get("originalText", "") == request.originalText:
                    doc.reference.update({
                        "originalText": request.originalText,
                        "convertedText": converted_text
                    })
                    logger.info(f"Updated document {doc.id} with converted text")
                    return {"convertedText": converted_text}

            raise HTTPException(status_code=404, detail="Document not found")
            
        except Exception as e:
            logger.error(f"Error converting text: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail=str(e))