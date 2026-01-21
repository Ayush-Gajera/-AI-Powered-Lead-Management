"""
AI Reply Scorer using OpenRouter API
Analyzes email replies and returns scoring, priority, and intent
"""
import json
import re
from typing import Dict, Optional
from pydantic import BaseModel, Field
from ai_provider import call_ai_model

class ReplyScoring(BaseModel):
    """AI scoring response model"""
    reply_score: int = Field(ge=0, le=100)
    priority: str = Field(pattern="^(HIGH|MEDIUM|LOW|IGNORE)$")
    intent: str
    confidence: float = Field(ge=0.0, le=1.0)
    reasons: list[str]


def clean_reply_text(reply_text: str) -> str:
    """
    Clean reply text by removing quoted history and signatures
    """
    # Remove lines starting with ">" (quoted text)
    lines = reply_text.split('\n')
    cleaned_lines = []
    
    for line in lines:
        # Skip quoted lines
        if line.strip().startswith('>'):
            continue
        # Skip lines with "On ... wrote:" pattern
        if re.search(r'On .+ wrote:', line):
            break
        # Skip common signature separators
        if line.strip() in ['--', '___', '---']:
            break
        cleaned_lines.append(line)
    
    cleaned_text = '\n'.join(cleaned_lines).strip()
    
    # Limit to first 2000 characters to avoid token limits
    return cleaned_text[:2000]


def score_reply_with_ai_model(reply_text: str) -> Optional[ReplyScoring]:
    """
    Score reply using OpenRouter AI
    Returns ReplyScoring object or None if failed
    """
    try:
        # Clean the reply text
        cleaned_text = clean_reply_text(reply_text)
        
        # Construct the prompt
        system_prompt = """
        You are an expert sales assistant. Analyze the incoming email reply and determine its value.
        
        Output Guide:
        - reply_score: 0-100
        - priority: HIGH (ready to buy/meet), MEDIUM (questions), LOW (not interested), IGNORE (spam/unsubscribe)
        - intent: INTERESTED, ASKING_PRICE, MEETING, NOT_INTERESTED, UNSUBSCRIBE, SPAM, OTHER
        - confidence: 0.0-1.0
        - reasons: List of short strings explaining why
        
        Rules:
        - Unsubscribe/Remove me -> IGNORE, Score <= 10
        - Not interested -> LOW
        - Pricing/Meeting -> HIGH
        
        Reply ONLY in JSON format matching the schema.
        """
        
        user_prompt = f"""
        Analyze this email reply:
        "{cleaned_text}"
        """

        # Call AI
        response_text = call_ai_model(
            prompt=user_prompt,
            system_message=system_prompt,
            json_mode=True
        )
        
        # Parse JSON
        data = json.loads(response_text)
        scoring = ReplyScoring(**data)
        
        print(f"✓ AI Scoring: {scoring.priority} ({scoring.reply_score}) - {scoring.intent}")
        return scoring
        
    except Exception as e:
        print(f"❌ AI Scoring Failed: {str(e)}")
        return None


def rule_based_score_reply(reply_text: str) -> ReplyScoring:
    """
    Fallback rule-based scoring when AI is unavailable
    """
    text_lower = reply_text.lower()
    score = 50
    priority = "MEDIUM"
    intent = "OTHER"
    confidence = 0.6
    reasons = []
    
    # Check for unsubscribe
    if any(word in text_lower for word in ['unsubscribe', 'remove me', 'stop emailing', 'opt out']):
        score = 5
        priority = "IGNORE"
        intent = "UNSUBSCRIBE"
        confidence = 0.95
        reasons = ["Contains unsubscribe request"]
        return ReplyScoring(
            reply_score=score,
            priority=priority,
            intent=intent,
            confidence=confidence,
            reasons=reasons
        )
    
    # Check for spam indicators
    if any(word in text_lower for word in ['viagra', 'casino', 'lottery', 'nigerian prince']):
        score = 0
        priority = "IGNORE"
        intent = "SPAM"
        confidence = 0.9
        reasons = ["Likely spam content"]
        return ReplyScoring(
            reply_score=score,
            priority=priority,
            intent=intent,
            confidence=confidence,
            reasons=reasons
        )
    
    # Check for high-interest keywords
    if any(word in text_lower for word in ['pricing', 'price', 'cost', 'quote', 'how much']):
        score = 85
        priority = "HIGH"
        intent = "ASKING_PRICE"
        confidence = 0.8
        reasons = ["Asking about pricing"]
    
    elif any(word in text_lower for word in ['meeting', 'call', 'schedule', 'demo', 'presentation']):
        score = 90
        priority = "HIGH"
        intent = "MEETING"
        confidence = 0.85
        reasons = ["Requesting meeting or demo"]
    
    elif any(word in text_lower for word in ['interested', 'tell me more', 'learn more', 'sounds good']):
        score = 75
        priority = "MEDIUM"
        intent = "INTERESTED"
        confidence = 0.7
        reasons = ["Expressed interest"]
    
    elif any(word in text_lower for word in ['not interested', 'no thank', 'not now', 'maybe later']):
        score = 25
        priority = "LOW"
        intent = "NOT_INTERESTED"
        confidence = 0.75
        reasons = ["Indicated not interested"]
    
    else:
        reasons = ["Generic reply - unclear intent"]
    
    return ReplyScoring(
        reply_score=score,
        priority=priority,
        intent=intent,
        confidence=confidence,
        reasons=reasons
    )


def score_reply_with_ai(reply_text: str) -> ReplyScoring:
    """
    Main function to score reply with AI or fallback to rules
    """
    # Try AI first
    ai_result = score_reply_with_ai_model(reply_text)
    
    if ai_result:
        return ai_result
    
    # Fallback to rule-based
    print("⚠ Using fallback rule-based scoring")
    return rule_based_score_reply(reply_text)
