from fastapi import APIRouter, Body
from pydantic import BaseModel
from get.parser import parse_transcript
from l1.claims import extract_claims
from l2.evidence import extract_evidence
from l3.verification import check_facts
from counter_response.analysis import analyze_rebuttals
from l4.scoring import generate_scores
from models.schemas import FinalEvaluation

router = APIRouter()

class TranscriptRequest(BaseModel):
    transcript_text: str

@router.post("/analyze", response_model=FinalEvaluation)
def analyze_debate(request: TranscriptRequest):
    # GET: Parse
    transcript = parse_transcript(request.transcript_text)
    
    # L1: Claims
    claims = extract_claims(transcript)
    
    # L2: Evidence
    evidence = extract_evidence(claims, transcript)
    
    # L3: Fact Checks
    fact_checks = check_facts(claims, evidence)
    
    # Counter-Response
    rebuttals = analyze_rebuttals(claims, transcript)
    
    # L4: Scoring
    final_evaluation = generate_scores(
        transcript=transcript,
        claims=claims,
        evidence=evidence,
        fact_checks=fact_checks,
        rebuttals=rebuttals
    )
    
    return final_evaluation
