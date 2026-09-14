import uuid
from typing import List
from models.schemas import TranscriptSegment, Transcript

def parse_transcript(raw_text: str) -> Transcript:
    """
    Splits the raw transcript text into segments by speaker.
    Expected format: 
    Speaker A: Hello
    Speaker B: Hi
    """
    lines = raw_text.strip().split('\n')
    segments = []
    
    current_speaker = None
    current_text = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Simple heuristic: looking for "SpeakerName:" or similar at the start of a line
        if ':' in line and len(line.split(':')[0]) < 25:
            # Save previous segment
            if current_speaker:
                segments.append(TranscriptSegment(
                    segment_id=str(uuid.uuid4()),
                    speaker=current_speaker,
                    text=" ".join(current_text)
                ))
            
            parts = line.split(':', 1)
            current_speaker = parts[0].strip()
            current_text = [parts[1].strip()]
        else:
            if current_speaker:
                current_text.append(line)
                
    # Add last segment
    if current_speaker:
        segments.append(TranscriptSegment(
            segment_id=str(uuid.uuid4()),
            speaker=current_speaker,
            text=" ".join(current_text)
        ))
        
    return Transcript(segments=segments)
