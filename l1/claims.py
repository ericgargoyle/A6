import json
import uuid
from typing import List
from models.schemas import Transcript, Claim
from api.ollama_client import ask_ollama

def extract_claims(transcript: Transcript) -> List[Claim]:
    claims = []
    for segment in transcript.segments:
        prompt = f"""
        Analyze the following text from the specified speaker and extract the main propositions or claims made.
        Return the result ONLY as a JSON array of objects.
        Each object should have:
        - "claim_text": The claim or assertion made.
        - "claim_type": The type of claim (factual, moral, policy, definition).
        
        Speaker: {segment.speaker}
        Text: "{segment.text}"
        """
        response_text = ask_ollama(prompt, json_format=True)
        try:
            extracted_data = json.loads(response_text)
            if not isinstance(extracted_data, list):
                if 'claims' in extracted_data:
                    extracted_data = extracted_data['claims']
                else:
                    extracted_data = [extracted_data]
            
            for item in extracted_data:
                if 'claim_text' in item and 'claim_type' in item:
                    claims.append(Claim(
                        claim_id=str(uuid.uuid4()),
                        speaker=segment.speaker,
                        segment_id=segment.segment_id,
                        claim_text=item['claim_text'],
                        claim_type=item['claim_type']
                    ))
        except json.JSONDecodeError:
            print(f"Failed to parse JSON from Ollama for L1 Claims: {response_text}")
    return claims
