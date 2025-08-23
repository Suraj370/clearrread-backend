import re
import requests
import logging
from config import get_gemini_api_url, GEMINI_CONFIG

logger = logging.getLogger(__name__)

def dyslexia_friendly_convert(text: str) -> str:
    """Convert text to dyslexia-friendly format using Google Gemini API."""
    if not text:
        logger.info("Input text is empty, returning empty string")
        return ""
    
    try:
        # Step 1: Call Google Gemini API
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

        headers = {"Content-Type": "application/json"}
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": GEMINI_CONFIG
        }
        
        response = requests.post(get_gemini_api_url(), headers=headers, json=payload)
        response.raise_for_status()
        response_data = response.json()
        logger.info(f"Raw Gemini API response: {response_data}")
        
        generated_text = response_data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", text).strip()
        if generated_text == text:
            logger.warning("Gemini API returned unchanged text")
        logger.info(f"Generated Gemini text: {generated_text}")

        # Step 2: Postprocess text
        processed_text = postprocess_text(generated_text)
        logger.info(f"Final converted text: {processed_text}")
        return processed_text
        
    except Exception as e:
        logger.error(f"Error in dyslexia_friendly_convert: {str(e)}", exc_info=True)
        # Fallback: Simple postprocessing of original text
        logger.info("Falling back to basic processing of original text")
        return postprocess_text(text)

def postprocess_text(text: str) -> str:
    """Postprocess text to ensure dyslexia-friendly formatting."""
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