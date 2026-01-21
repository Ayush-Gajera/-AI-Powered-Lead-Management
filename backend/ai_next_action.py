"""
AI Next Best Action Generator using OpenRouter API
Suggests actionable next steps based on email reply analysis
"""
import json
from typing import Dict, Optional
from pydantic import BaseModel, Field
from ai_provider import call_ai_model

class NextActionResponse(BaseModel):
    """Next Best Action model"""
    next_action_title: str
    next_action_steps: list[str]
    urgency: str = Field(pattern="^(NOW|TODAY|THIS_WEEK)$")
    followup_days: int = Field(ge=0, le=30)
    suggested_tone: str = Field(pattern="^(FORMAL|FRIENDLY|SHORT)$")


def generate_next_action_with_ai(
    reply_text: str,
    intent: str,
    score: int,
    priority: str,
    lead_name: str,
    lead_company: Optional[str] = None,
    outbound_subject: Optional[str] = None,
    outbound_body: Optional[str] = None
) -> Optional[NextActionResponse]:
    """
    Generate next best action using OpenRouter AI
    """
    try:
        # Build prompt
        context = f"""
        Lead: {lead_name}
        Company: {lead_company or 'Unknown'}
        Intent: {intent}
        Priority: {priority}
        Score: {score}/100
        Original Subject: {outbound_subject or 'N/A'}
        """
        
        system_prompt = """
        You are a sales action strategist. Based on the email reply analysis, suggest the next best action.
        
        Output Guide:
        - next_action_title: Max 60 chars (e.g., "Send Pricing", "Schedule Call")
        - next_action_steps: List of 3 specific, actionable steps
        - urgency: NOW (hot lead), TODAY (warm), THIS_WEEK (cold/nurture)
        - followup_days: 1-7 days
        - suggested_tone: FORMAL, FRIENDLY, SHORT
        
        Reply strictly in valid JSON matching the schema.
        """
        
        user_prompt = f"""
        Context:
        {context}
        
        Reply Content:
        "{reply_text[:1000]}"
        
        Suggest the next best action in JSON.
        """

        # Call AI
        response_text = call_ai_model(
            prompt=user_prompt,
            system_message=system_prompt,
            json_mode=True
        )
        
        # Parse JSON
        data = json.loads(response_text)
        action = NextActionResponse(**data)
        print(f"✓ AI Next Action: {action.next_action_title}")
        return action
        
    except Exception as e:
        print(f"❌ AI Next Action Failed: {str(e)}")
        return None


def generate_fallback_next_action(
    intent: str,
    priority: str,
    lead_name: str
) -> NextActionResponse:
    """
    Fallback next action generator based on intent
    """
    intent_actions = {
        "ASKING_PRICE": NextActionResponse(
            next_action_title="Send Pricing Information",
            next_action_steps=[
                "Prepare pricing document",
                "Ask about budget and timeline",
                "Follow up in 24 hours"
            ],
            urgency="NOW",
            followup_days=1,
            suggested_tone="FORMAL"
        ),
        "MEETING": NextActionResponse(
            next_action_title="Schedule Meeting",
            next_action_steps=[
                "Share calendar link",
                "Propose time slots",
                "Send meeting agenda"
            ],
            urgency="NOW",
            followup_days=1,
            suggested_tone="FRIENDLY"
        ),
        "INTERESTED": NextActionResponse(
            next_action_title="Provide More Information",
            next_action_steps=[
                "Send product details",
                "Share case studies",
                "Ask qualifying questions"
            ],
            urgency="TODAY",
            followup_days=2,
            suggested_tone="FRIENDLY"
        ),
        "NOT_INTERESTED": NextActionResponse(
            next_action_title="Close Gracefully",
            next_action_steps=[
                "Thank for their time",
                "Ask if may contact in future",
                "Request referrals if appropriate"
            ],
            urgency="THIS_WEEK",
            followup_days=7,
            suggested_tone="SHORT"
        ),
        "UNSUBSCRIBE": NextActionResponse(
            next_action_title="Mark Do Not Contact",
            next_action_steps=[
                "Remove from email list",
                "Update CRM status",
                "Respect unsubscribe request"
            ],
            urgency="NOW",
            followup_days=0,
            suggested_tone="FORMAL"
        ),
    }
    
    # Return intent-specific action or generic
    return intent_actions.get(intent, NextActionResponse(
        next_action_title="Follow Up",
        next_action_steps=[
            "Review their response",
            "Prepare personalized follow-up",
            "Send within 2-3 days"
        ],
        urgency="TODAY",
        followup_days=3,
        suggested_tone="FRIENDLY"
    ))


def generate_next_action(
    reply_text: str,
    intent: str,
    score: int,
    priority: str,
    lead_name: str,
    lead_company: Optional[str] = None,
    outbound_subject: Optional[str] = None,
    outbound_body: Optional[str] = None
) -> NextActionResponse:
    """
    Main function to generate next action with AI or fallback
    """
    # Try AI first
    ai_result = generate_next_action_with_ai(
        reply_text=reply_text,
        intent=intent,
        score=score,
        priority=priority,
        lead_name=lead_name,
        lead_company=lead_company,
        outbound_subject=outbound_subject,
        outbound_body=outbound_body
    )
    
    if ai_result:
        return ai_result
    
    # Fallback
    print("⚠ Using fallback next action generation")
    return generate_fallback_next_action(intent, priority, lead_name)
