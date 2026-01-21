"""
AI Reply Scorer using Google Gemini Flash 2.0
Analyzes email replies and returns scoring, priority, and intent
"""
import os
import json
import re
from typing import Dict, Optional
from dotenv import load_dotenv
import google.generativeai as genai
from pydantic import BaseModel, Field

load_dotenv()

# Gemini Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash-exp")

# Configure Gemini
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)


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


def extract_json_from_response(response_text: str) -> Optional[Dict]:
    """
    Extract JSON block from Gemini response
    Handles cases where Gemini adds extra text around JSON
    """
    # Try to find JSON block in markdown code fence
    json_match = re.search(r'```(?:json)?\s*(\{.+?\})\s*```', response_text, re.DOTALL)
    if json_match:
        try:
            return json.loads(json_match.group(1))
        except json.JSONDecodeError:
            pass
    
    # Try to find raw JSON object
    json_match = re.search(r'\{[\s\S]*\}', response_text)
    if json_match:
        try:
            return json.loads(json_match.group(0))
        except json.JSONDecodeError:
            pass
    
    # Try to parse entire response as JSON
    try:
        return json.loads(response_text)
    except json.JSONDecodeError:
        return None


def score_reply_with_gemini(reply_text: str) -> Optional[ReplyScoring]:
    """
    Score reply using Google Gemini Flash 2.0
    Returns ReplyScoring object or None if failed
    """
    if not GEMINI_API_KEY:
        print("Warning: GEMINI_API_KEY not configured, using fallback scoring")
        return None
    
    try:
        # Clean the reply text
        cleaned_text = clean_reply_text(reply_text)
        
        # Construct the prompt
        prompt = f"""You are an expert sales assistant. Analyze the following email reply and decide if it is a valuable lead reply.

Return ONLY valid JSON with this schema:
{{
"reply_score": number (0-100),
"priority": "HIGH" | "MEDIUM" | "LOW" | "IGNORE",
"intent": "INTERESTED" | "ASKING_PRICE" | "MEETING" | "NOT_INTERESTED" | "UNSUBSCRIBE" | "SPAM" | "OTHER",
"confidence": number (0.0-1.0),
"reasons": string[]
}}

Rules:
- HIGH (80-100): wants pricing, demo, meeting, ready to buy, urgent.
- MEDIUM (50-79): asks for details, maybe later, needs follow-up.
- LOW (20-49): vague reply, not clear intent.
- IGNORE (0-19): unsubscribe, spam, abusive, irrelevant.

If the reply contains unsubscribe request → priority must be IGNORE and score <= 10.
If the reply says not interested → priority LOW or IGNORE depending on tone.

Be concise. Reasons must be short bullet-like strings.

Now analyze this email reply:
{cleaned_text}"""

        # Initialize model
        model = genai.GenerativeModel(GEMINI_MODEL)
        
        # Configure generation with timeout
        generation_config = {
            "temperature": 0.3,  # Lower temperature for more consistent output
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 500,
        }
        
        # Generate response with retry logic
        max_retries = 2
        for attempt in range(max_retries + 1):
            try:
                response = model.generate_content(
                    prompt,
                    generation_config=generation_config,
                    request_options={"timeout": 10}  # 10 second timeout
                )
                
                # Extract text from response
                response_text = response.text
                
                # Extract JSON from response
                json_data = extract_json_from_response(response_text)
                
                if json_data:
                    # Validate and parse with Pydantic
                    scoring = ReplyScoring(**json_data)
                    return scoring
                else:
                    print(f"Warning: Could not extract JSON from Gemini response (attempt {attempt + 1})")
                    if attempt < max_retries:
                        continue
                    return None
                    
            except Exception as e:
                print(f"Error calling Gemini API (attempt {attempt + 1}): {str(e)}")
                if attempt < max_retries:
                    continue
                return None
        
        return None
        
    except Exception as e:
        print(f"Error in score_reply_with_gemini: {str(e)}")
        return None


def rule_based_score_reply(reply_text: str) -> ReplyScoring:
    """
    Fallback rule-based scoring when Gemini is unavailable
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
    Main function to score reply with AI (Gemini) or fallback to rules
    """
    # Try Gemini first
    gemini_result = score_reply_with_gemini(reply_text)
    
    if gemini_result:
        print(f"✓ Gemini scoring successful: {gemini_result.priority} ({gemini_result.reply_score})")
        return gemini_result
    
    # Fallback to rule-based
    print("⚠ Using fallback rule-based scoring")
    return rule_based_score_reply(reply_text)
