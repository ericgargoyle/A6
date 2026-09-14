import json
import uuid
from typing import List
from models.schemas import Transcript, Claim
from api.ollama_client import ask_ollama

def extract_claims(transcript: Transcript) -> List[Claim]:
    transcript_payload = [
        {"segment_id": s.segment_id, "speaker": s.speaker, "text": s.text}
        for s in transcript.segments
    ]
    
    prompt = f"""
    Analyze the full debate transcript and extract key arguments and claims made by each speaker.
    Return ONLY a JSON array of objects where each object has:
    - "segment_id": matching the segment where it occurred
    - "speaker": speaker name
    - "claim_text": concise statement of the proposition
    - "claim_type": "factual", "moral", "policy", or "definition"

    Transcript:
    {json.dumps(transcript_payload)}
    """
    
    response_text = ask_ollama(prompt, json_format=True)
    claims = []
    try:
        items = json.loads(response_text)
        if isinstance(items, dict) and "claims" in items:
            items = items["claims"]
        for it in items:
            claims.append(Claim(
                claim_id=str(uuid.uuid4()),
                speaker=it["speaker"],
                segment_id=it["segment_id"],
                claim_text=it["claim_text"],
                claim_type=it.get("claim_type", "factual")
            ))
    except Exception as e:
        print(f"Batch claims extraction error: {e}")
    return claims
