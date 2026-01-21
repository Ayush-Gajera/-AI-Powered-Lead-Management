"""
AI Draft Reply Generator using OpenRouter API
Generates professional email replies with customizable tone
"""
import json
from typing import Dict, Optional, List
from pydantic import BaseModel
from ai_provider import call_ai_model

class DraftReplyResponse(BaseModel):
    """Draft Reply model"""
    subject: str
    body: str


def generate_draft_with_ai(
    lead_name: str,
    lead_company: Optional[str],
    reply_text: str,
    intent: str,
    next_action_steps: List[str],
    tone: str = "FRIENDLY",
    attachments: Optional[List[Dict]] = None,
    original_subject: Optional[str] = None
) -> Optional[DraftReplyResponse]:
    """
    Generate draft reply using OpenRouter AI
    """
    try:
        # Build tone guidance
        tone_guidance = {
            "FORMAL": "Use professional, formal language. Address as Mr./Ms. Be polite and structured.",
            "FRIENDLY": "Use warm, conversational tone. Be professional but approachable. Use first name.",
            "SHORT": "Be concise and to-the-point. Keep under 8 lines. Direct but polite."
        }
        
        tone_instruction = tone_guidance.get(tone, tone_guidance["FRIENDLY"])
        
        # Build attachment mention
        attachment_text = ""
        if attachments and len(attachments) > 0:
            file_names = [att.get('file_name', 'attachment') for att in attachments]
            if len(file_names) == 1:
                attachment_text = f"\nMention the attached file: {file_names[0]}"
            else:
                attachment_text = f"\nMention the attached files: {', '.join(file_names)}"
        
        # Build action context
        action_context = ""
        if next_action_steps:
            action_context = "\nNext steps to cover:\n"
            for step in next_action_steps[:3]:  # Max 3 steps
                action_context += f"- {step}\n"
        
        # Construct prompt
        system_prompt = f"""
        You are an expert business email writer. Draft a professional reply to the email below.
        
        Context:
        Lead: {lead_name}
        Company: {lead_company or 'Unknown'}
        Intent: {intent}
        Tone: {tone_instruction}
        {attachment_text}
        
        Rules:
        - Start with greeting
        - 5-12 lines max (unless SHORT tone)
        - Ask 1-3 relevant questions
        - Include {{MEETING_LINK}} if needing to schedule
        - Plain text only
        
        Reply ONLY in JSON format:
        {{
            "subject": "Re: ...",
            "body": "plain text email body"
        }}
        """
        
        user_prompt = f"""
        Their message:
        "{reply_text[:800]}"
        
        {action_context}
        
        Draft the reply in JSON.
        """

        # Call AI
        response_text = call_ai_model(
            prompt=user_prompt,
            system_message=system_prompt,
            json_mode=True
        )
        
        # Parse JSON
        data = json.loads(response_text)
        draft = DraftReplyResponse(**data)
        
        # Ensure subject starts with Re: if not already
        if original_subject and not draft.subject.startswith("Re:"):
            draft.subject = f"Re: {original_subject}"
        
        print(f"✓ AI draft generated ({tone} tone)")
        return draft
        
    except Exception as e:
        print(f"❌ AI Draft Gen Failed: {str(e)}")
        return None


def generate_fallback_draft(
    lead_name: str,
    intent: str,
    tone: str,
    attachments: Optional[List[Dict]] = None,
    original_subject: Optional[str] = None
) -> DraftReplyResponse:
    """
    Fallback draft generator based on intent and tone
    """
    greeting = f"Hi {lead_name}," if tone in ["FRIENDLY", "SHORT"] else f"Dear {lead_name},"
    
    # Build body based on intent
    if intent == "ASKING_PRICE":
        body = f"""{greeting}

Thank you for your interest in our solution.

I've attached our pricing information for your review. Our plans are designed to scale with your needs.

Could you share more about your specific requirements and timeline? This will help me recommend the best fit for your team.

Happy to answer any questions you have.

Best regards"""
    
    elif intent == "MEETING":
        body = f"""{greeting}

I'd be happy to schedule a meeting to discuss this further.

You can book a time that works best for you here: {{MEETING_LINK}}

Alternatively, let me know your availability and I'll send an invite.

Looking forward to connecting!

Best regards"""
    
    elif intent == "INTERESTED":
        body = f"""{greeting}

Thank you for your interest! I'm excited to share more details with you.

I've attached some information that should be helpful. Our solution helps teams streamline their workflow and increase productivity.

What specific challenges are you looking to address? I'd love to tailor the conversation to your needs.

Best regards"""
    
    elif intent == "NOT_INTERESTED":
        body = f"""{greeting}

Thank you for taking the time to respond.

I completely understand. If your needs change in the future, please don't hesitate to reach out.

If you know anyone who might benefit from our solution, I'd appreciate an introduction.

Best regards"""
    
    else:  # Generic
        body = f"""{greeting}

Thank you for your message.

I appreciate you taking the time to reply. Let me know if there's anything I can help with or any information you need.

Looking forward to hearing from you.

Best regards"""
    
    # Add attachment mention if present
    if attachments and len(attachments) > 0:
        file_names = [att.get('file_name', 'document') for att in attachments]
        if "attached" not in body:
            file_list = file_names[0] if len(file_names) == 1 else ", ".join(file_names)
            body = body.replace(
                "Best regards",
                f"I've attached {file_list} for your reference.\n\nBest regards"
            )
    
    # Shorten if SHORT tone
    if tone == "SHORT":
        lines = body.split('\n')
        body = '\n'.join([l for l in lines if l.strip()])[:300]
    
    subject = f"Re: {original_subject}" if original_subject else "Re: Your inquiry"
    
    return DraftReplyResponse(subject=subject, body=body)


def generate_draft_reply(
    lead_name: str,
    lead_company: Optional[str],
    reply_text: str,
    intent: str,
    next_action_steps: List[str],
    tone: str = "FRIENDLY",
    attachments: Optional[List[Dict]] = None,
    original_subject: Optional[str] = None
) -> DraftReplyResponse:
    """
    Main function to generate draft reply with AI or fallback
    """
    # Try AI first
    ai_result = generate_draft_with_ai(
        lead_name=lead_name,
        lead_company=lead_company,
        reply_text=reply_text,
        intent=intent,
        next_action_steps=next_action_steps,
        tone=tone,
        attachments=attachments,
        original_subject=original_subject
    )
    
    if ai_result:
        return ai_result
    
    # Fallback
    print("⚠ Using fallback draft generation")
    return generate_fallback_draft(
        lead_name=lead_name,
        intent=intent,
        tone=tone,
        attachments=attachments,
        original_subject=original_subject
    )
