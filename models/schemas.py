from pydantic import BaseModel, Field
from typing import List, Optional, Dict

class TranscriptSegment(BaseModel):
    segment_id: str
    speaker: str
    text: str

class Transcript(BaseModel):
    segments: List[TranscriptSegment]

class Claim(BaseModel):
    claim_id: str
    speaker: str
    segment_id: str
    claim_text: str
    claim_type: str = Field(description="e.g., factual, moral, policy, definition")

class Evidence(BaseModel):
    evidence_id: str
    claim_id: str
    speaker: str
    evidence_text: str
    source: Optional[str] = None
    evidence_type: str = Field(description="e.g., statistic, quote, anecdote, study")

class FactCheckResult(BaseModel):
    claim_id: str
    status: str = Field(description="supported, unsupported, questionable, contradicted")
    source_url: Optional[str] = None
    reasoning: str

class Rebuttal(BaseModel):
    rebuttal_id: str
    responding_speaker: str
    target_claim_id: str
    rebuttal_text: str
    type: str = Field(description="direct, deflection, concession")
    survived: Optional[bool] = None

class SpeakerScore(BaseModel):
    logical_consistency: int
    evidence_quality: int
    rebuttal_strength: int
    relevance: int
    clarity: int
    overall: int

class FinalEvaluation(BaseModel):
    speaker_a: SpeakerScore
    speaker_b: SpeakerScore
    winner: str
    reason: str
