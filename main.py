from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import firebase_admin
from firebase_admin import credentials, firestore
from pydantic import BaseModel
import re
import requests
import logging
import os
from google.cloud.firestore_v1 import DocumentReference
from dotenv import load_dotenv
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Firebase Admin SDK
cred = credentials.Certificate("serviceAccount.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("FRONTEND_URL", "http://localhost:3000")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class DocumentRequest(BaseModel):
    userId: str
    name: str | None = None
    originalText: str | None = None

class RenameRequest(BaseModel):
    userId: str
    docId: str
    oldName: str
    newName: str

# Helper function to convert Firestore data to JSON-serializable format
def firestore_to_json(data: dict) -> dict:
    """Convert Firestore document data to JSON-serializable format."""
    result = {}
    for key, value in data.items():
        if isinstance(value, DocumentReference):
            result[key] = value.id
        else:
            result[key] = value
    return result

# Text conversion function using Google Gemini API
def dyslexia_friendly_convert(text: str) -> str:
    if not text:
        logger.info("Input text is empty, returning empty string")
        return ""
    
    try:
        # Step 1: Call Google Gemini API
        api_key = os.getenv("GEMINI_API_KEY", "Your-Gemini-API-KEY")
        api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"
        prompt = (
            f"Rewrite the entire text below for dyslexic readers. "
            f"Use short sentences, each with no more than 15 words. "
            f"Replace all complex or academic words with very simple, common words (e.g., 'utilizing' to 'using', 'elucidates' to 'explains'). "
            f"Ensure extremely clear and concise language for maximum readability. "
            f"Preserve every detail and fact from the original text, including numbers and percentages. "
            f"Do not summarize; rewrite every sentence to include all information. "
            f"Example: 'Approximately eighty percent of the economy' becomes 'About 80% of the economy'. "
            f"Here is the text:\n\n"
            f"{text}"
        )
        logger.info(f"Gemini API prompt: {prompt}")

        headers = {
            "Content-Type": "application/json"
        }
        payload = {
            "contents": [{
                "parts": [{"text": prompt}]
            }],
            "generationConfig": {
                "temperature": 0.7,
                "maxOutputTokens": 1000,  # Increased to handle longer outputs
                "topP": 1.0
            }
        }
        response = requests.post(api_url, headers=headers, json=payload)
        response.raise_for_status()
        response_data = response.json()
        logger.info(f"Raw Gemini API response: {response_data}")
        generated_text = response_data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", text).strip()
        if generated_text == text:
            logger.warning("Gemini API returned unchanged text")
        logger.info(f"Generated Gemini text: {generated_text}")

        # Step 2: Postprocess text
        def postprocess_text(text):
            logger.info("Starting postprocessing")
            # Normalize case for consistent capitalization
            text = text.lower()
            text = re.sub(r'b(?![h])', 'B', text)
            text = re.sub(r'd', 'D', text)
            # Split into sentences, handling various punctuation
            sentences = re.split(r'(?<=[.!?])\s+', text.strip())
            final_sentences = []
            for sentence in sentences:
                words = sentence.split()
                if not words:
                    continue
                if len(words) <= 15:
                    final_sentences.append(sentence)
                else:
                    # Split long sentences at logical points (e.g., commas, conjunctions)
                    chunks = []
                    current_chunk = []
                    word_count = 0
                    for word in words:
                        current_chunk.append(word)
                        word_count += 1
                        if word_count >= 10 or word in [',', 'and', 'or', 'but']:
                            chunk_text = " ".join(current_chunk)
                            if chunk_text:
                                chunks.append(chunk_text)
                            current_chunk = []
                            word_count = 0
                    if current_chunk:
                        chunk_text = " ".join(current_chunk)
                        if chunk_text:
                            chunks.append(chunk_text)
                    final_sentences.extend(chunks)
            # Ensure sentences end with punctuation and are non-empty
            final_sentences = [s + ('.' if not s.endswith(('.', '!', '?')) else '') for s in final_sentences if s.strip()]
            logger.info(f"Postprocessed sentences: {final_sentences}")
            return "\n\n".join(final_sentences)

        processed_text = postprocess_text(generated_text)
        logger.info(f"Final converted text: {processed_text}")
        return processed_text
    except Exception as e:
        logger.error(f"Error in dyslexia_friendly_convert: {str(e)}", exc_info=True)
        # Fallback: Simple postprocessing of original text
        logger.info("Falling back to basic processing of original text")
        return postprocess_text(text)

# API Endpoints
@app.post("/create-document/")
async def create_document(request: DocumentRequest):
    try:
        documents_ref = db.collection("documents")
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

@app.post("/rename-document/")
async def rename_document(request: RenameRequest):
    try:
        documents_ref = db.collection("documents")
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

@app.post("/convert-text/")
async def convert_text(request: DocumentRequest):
    try:
        if not request.originalText:
            raise HTTPException(status_code=400, detail="Original text is required")

        logger.info(f"Received text for conversion: {request.originalText}")
        converted_text = dyslexia_friendly_convert(request.originalText)
        logger.info(f"Converted text: {converted_text}")

        documents_ref = db.collection("documents")
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)