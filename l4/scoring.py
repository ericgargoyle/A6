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
    # 1. Preserve original appearance order (Step 1)
    speakers = list(dict.fromkeys([seg.speaker for seg in transcript.segments]))
    if len(speakers) < 2:
        speakers = ["Speaker A", "Speaker B"]
    speaker_a, speaker_b = speakers[0], speakers[1]

    # 2. Map evidence and verification by claim ID
    ev_map = {e.claim_id: e for e in evidence}
    fc_map = {fc.claim_id: fc for fc in fact_checks}

    def compile_speaker_case(spk):
        case = []
        spk_claims = [c for c in claims if c.speaker == spk]
        for c in spk_claims:
            ev = ev_map.get(c.claim_id)
            fc = fc_map.get(c.claim_id)
            case.append({
                "claim": c.claim_text,
                "type": c.claim_type,
                "evidence": ev.evidence_text if ev else "No evidence cited",
                "verification": fc.status if fc else "unverified"
            })
        return case

    rebuttal_summary = [
        {
            "responder": r.responding_speaker,
            "target_claim_id": r.target_claim_id,
            "argument": r.rebuttal_text,
            "effective": r.survived
        }
        for r in rebuttals
    ]

    detailed_data = {
        speaker_a: compile_speaker_case(speaker_a),
        speaker_b: compile_speaker_case(speaker_b),
        "rebuttals": rebuttal_summary
    }

    prompt = f"""
    You are an impartial, elite debate adjudicator. Evaluate the debate between {speaker_a} and {speaker_b}.
    Score each speaker from 0 to 100 on these metrics:
    - logical_consistency: Coherence and lack of contradictions/fallacies.
    - evidence_quality: Reliance on verified, credible facts vs unsupported assertions.
    - rebuttal_strength: Directly dismantling the opponent's core points.
    - relevance: Staying on topic without deflection.
    - clarity: Articulation and structure.
    - overall: Weighted synthesis of argument performance.

    Debate Evidence & Claims:
    {json.dumps(detailed_data, indent=2)}

    Requirements:
    1. Base scores strictly on the provided evidence verification and rebuttals above.
    2. The 'reason' MUST quote or reference specific claims or failed arguments to defend why the winner won.
    3. Return ONLY valid JSON matching this schema:
    {{
      "speaker_a": {{
        "logical_consistency": <int>, "evidence_quality": <int>, "rebuttal_strength": <int>,
        "relevance": <int>, "clarity": <int>, "overall": <int>
      }},
      "speaker_b": {{
        "logical_consistency": <int>, "evidence_quality": <int>, "rebuttal_strength": <int>,
        "relevance": <int>, "clarity": <int>, "overall": <int>
      }},
      "winner": "{speaker_a}" or "{speaker_b}",
      "reason": "<Detailed justification citing specific arguments>"
    }}
    """

    response_text = ask_ollama(prompt, json_format=True)
    try:
        data = json.loads(response_text)
        s_a = data.get("speaker_a") or data.get(speaker_a, {})
        s_b = data.get("speaker_b") or data.get(speaker_b, {})

        return FinalEvaluation(
            speaker_a=s_a,
            speaker_b=s_b,
            winner=data.get("winner", "Tie"),
            reason=data.get("reason", "Evaluation complete.")
        )
    except Exception as e:
        print(f"Scoring parsing error: {e}")
        return FinalEvaluation(
            speaker_a={"logical_consistency": 50, "evidence_quality": 50, "rebuttal_strength": 50, "relevance": 50, "clarity": 50, "overall": 50},
            speaker_b={"logical_consistency": 50, "evidence_quality": 50, "rebuttal_strength": 50, "relevance": 50, "clarity": 50, "overall": 50},
            winner="Tie",
            reason="Model output parsing failed."
        )