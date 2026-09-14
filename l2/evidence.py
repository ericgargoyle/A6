import json
import uuid
from typing import List, Dict
from models.schemas import Claim, Evidence, Transcript
from api.ollama_client import ask_ollama

def extract_evidence(claims: List[Claim], transcript: Transcript) -> List[Evidence]:
    all_evidence = []
    
    # We will pass the full segment text corresponding to the claim to extract evidence
    segment_map = {seg.segment_id: seg.text for seg in transcript.segments}
    
    for claim in claims:
        segment_text = segment_map.get(claim.segment_id, "")
        prompt = f"""
        Analyze the following claim and the accompanying source context.
        Identify any evidence, citations, data, or supporting material provided to support the claim.
        Return the result ONLY as a JSON array of objects.
        If no supporting evidence is provided, return an empty array [].
        Each object should have:
        - "evidence_text": The text of the supporting evidence.
        - "source": The cited source or attribution (if explicitly mentioned, otherwise null).
        - "evidence_type": Type of evidence (statistic, quote, anecdote, study).
        
        Claim: "{claim.claim_text}"
        Context: "{segment_text}"
        """
        response_text = ask_ollama(prompt, json_format=True)
        try:
            extracted_data = json.loads(response_text)
            if not isinstance(extracted_data, list):
                if 'evidence' in extracted_data:
                    extracted_data = extracted_data['evidence']
                else:
                    extracted_data = [extracted_data]
            
            for item in extracted_data:
                if 'evidence_text' in item and 'evidence_type' in item:
                    all_evidence.append(Evidence(
                        evidence_id=str(uuid.uuid4()),
                        claim_id=claim.claim_id,
                        speaker=claim.speaker,
                        evidence_text=item['evidence_text'],
                        source=item.get('source'),
                        evidence_type=item['evidence_type']
                    ))
        except json.JSONDecodeError:
            print(f"Failed to parse JSON from Ollama for L2 Evidence: {response_text}")
            
    return all_evidence
