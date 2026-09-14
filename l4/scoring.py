import json
from typing import List
from models.schemas import FinalEvaluation, Claim, Evidence, FactCheckResult, Rebuttal, Transcript
from api.ollama_client import ask_ollama

def generate_scores(
    transcript: Transcript,
    claims: List[Claim],
    evidence: List[Evidence],
    fact_checks: List[FactCheckResult],
    rebuttals: List[Rebuttal]
) -> FinalEvaluation:
    
    speakers = list(set([seg.speaker for seg in transcript.segments]))
    if len(speakers) < 2:
        speakers = ["Speaker A", "Speaker B"] # Default if only one or zero found
        
    speaker_a, speaker_b = speakers[0], speakers[1]
    
    # Summarize data for the prompt
    data_summary = {
        "claims_count": len(claims),
        "evidence_count": len(evidence),
        "fact_checks": [{"id": fc.claim_id, "status": fc.status} for fc in fact_checks],
        "rebuttals_count": len(rebuttals)
    }
    
    prompt = f"""
    You are an objective analytical evaluator. Analyze the provided summary of claims, evidence, verification results, and responses between the two speakers.
    Generate integer evaluation scores (from 0 to 100) for each speaker across the evaluation dimensions.
    The determination of the leading speaker must depend strictly on logic, evidence quality, and response strength.
    
    Speakers: {speaker_a} and {speaker_b}
    Analysis Summary: {json.dumps(data_summary)}
    
    Return ONLY a JSON object conforming exactly to this structure:
    {{
      "speaker_a": {{
        "logical_consistency": <integer between 0 and 100>,
        "evidence_quality": <integer between 0 and 100>,
        "rebuttal_strength": <integer between 0 and 100>,
        "relevance": <integer between 0 and 100>,
        "clarity": <integer between 0 and 100>,
        "overall": <integer between 0 and 100>
      }},
      "speaker_b": {{
        "logical_consistency": <integer between 0 and 100>,
        "evidence_quality": <integer between 0 and 100>,
        "rebuttal_strength": <integer between 0 and 100>,
        "relevance": <integer between 0 and 100>,
        "clarity": <integer between 0 and 100>,
        "overall": <integer between 0 and 100>
      }},
      "winner": "Name of the winning speaker",
      "reason": "Brief explanation of the outcome based on the metrics"
    }}
    
    Note: Substitute "speaker_a" and "speaker_b" keys with the actual speaker names: "{speaker_a}" and "{speaker_b}". 
    Or you can keep keys as "speaker_a" and "speaker_b" but ensure the winner matches one of them.
    """
    
    response_text = ask_ollama(prompt, json_format=True)
    try:
        data = json.loads(response_text)
        
        # Mapping back keys if the model used actual names
        s_a_key = "speaker_a" if "speaker_a" in data else speaker_a
        s_b_key = "speaker_b" if "speaker_b" in data else speaker_b
        
        return FinalEvaluation(
            speaker_a=data.get(s_a_key, {}),
            speaker_b=data.get(s_b_key, {}),
            winner=data.get("winner", "Tie"),
            reason=data.get("reason", "Could not determine.")
        )
    except json.JSONDecodeError:
        print(f"Failed to parse L4 Scoring JSON: {response_text}")
        # Return mock data on failure to prevent total crash
        return FinalEvaluation(
            speaker_a={"logical_consistency": 0, "evidence_quality": 0, "rebuttal_strength": 0, "relevance": 0, "clarity": 0, "overall": 0},
            speaker_b={"logical_consistency": 0, "evidence_quality": 0, "rebuttal_strength": 0, "relevance": 0, "clarity": 0, "overall": 0},
            winner="Unknown",
            reason="Analysis failed."
        )
