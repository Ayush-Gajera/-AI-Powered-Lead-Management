"""
API routes for reply syncing
"""
from fastapi import APIRouter, HTTPException
from models import SyncRepliesResponse
from db import supabase
from imap_tracker import scan_inbox_for_replies
from ai_reply_scorer import score_reply_with_ai

router = APIRouter(prefix="/sync", tags=["sync"])


def get_priority_rank(priority: str) -> int:
    """Get numeric rank for priority comparison"""
    rank_map = {"HIGH": 4, "MEDIUM": 3, "LOW": 2, "IGNORE": 1}
    return rank_map.get(priority, 0)


@router.post("/replies", response_model=SyncRepliesResponse)
async def sync_replies():
    """
    Scan inbox for replies and update database with AI scoring
    Uses In-Reply-To and References headers to match replies
    """
    try:
        # Get all outbound emails with their message IDs
        outbound_response = supabase.table("outbound_emails").select("id, message_id, lead_id").execute()
        
        if not outbound_response.data:
            return SyncRepliesResponse(
                success=True,
                replies_found=0,
                message="No outbound emails found"
            )
        
        # Build mapping of message_id -> outbound_email
        message_id_map = {
            email['message_id']: email
            for email in outbound_response.data
        }
        
        # Get list of message IDs to check
        outbound_message_ids = list(message_id_map.keys())
        
        # Scan inbox for replies
        replies = scan_inbox_for_replies(outbound_message_ids)
        
        replies_found = 0
        
        # Process each reply
        for reply in replies:
            matched_message_id = reply['matched_message_id']
            outbound_email = message_id_map.get(matched_message_id)
            
            if not outbound_email:
                continue
            
            # Check if this reply already exists (idempotent)
            existing_reply = supabase.table("inbound_replies").select("id").eq(
                "outbound_email_id", outbound_email['id']
            ).eq("from_email", reply['from_email']).execute()
            
            if existing_reply.data:
                # Reply already recorded, skip
                continue
            
            # === AI SCORING ===
            # Score the reply using Gemini AI or fallback
            scoring = score_reply_with_ai(reply['body_preview'])
            
            # Insert new reply with AI scoring
            reply_data = {
                "lead_id": outbound_email['lead_id'],
                "outbound_email_id": outbound_email['id'],
                "from_email": reply['from_email'],
                "subject": reply['subject'],
                "body_preview": reply['body_preview'],
                "received_at": reply['received_at'],
                # AI scoring fields
                "reply_score": scoring.reply_score,
                "priority": scoring.priority,
                "intent": scoring.intent,
                "confidence": scoring.confidence,
                "reasons": scoring.reasons  # JSONB field
            }
            
            supabase.table("inbound_replies").insert(reply_data).execute()
            
            # Update outbound email with scoring summary
            supabase.table("outbound_emails").update({
                "is_replied": True,
                "reply_score": scoring.reply_score,
                "priority": scoring.priority,
                "intent": scoring.intent,
                "confidence": scoring.confidence
            }).eq("id", outbound_email['id']).execute()
            
            # === UPDATE LEAD SCORING ===
            # Get current lead data
            lead_response = supabase.table("leads").select("*").eq("id", outbound_email['lead_id']).execute()
            
            if lead_response.data:
                current_lead = lead_response.data[0]
                current_score = current_lead.get('lead_score', 0)
                current_priority = current_lead.get('lead_priority', 'LOW')
                
                # Calculate new lead score (max of all replies)
                new_lead_score = max(current_score, scoring.reply_score)
                
                # Determine new lead priority (highest priority wins)
                current_priority_rank = get_priority_rank(current_priority)
                new_priority_rank = get_priority_rank(scoring.priority)
                new_lead_priority = scoring.priority if new_priority_rank > current_priority_rank else current_priority
                
                # Update lead with aggregated scoring
                supabase.table("leads").update({
                    "status": "REPLIED",
                    "last_replied_at": reply['received_at'],
                    "lead_score": new_lead_score,
                    "lead_priority": new_lead_priority,
                    "last_reply_score": scoring.reply_score,
                    "last_reply_intent": scoring.intent
                }).eq("id", outbound_email['lead_id']).execute()
            
            replies_found += 1
        
        return SyncRepliesResponse(
            success=True,
            replies_found=replies_found,
            message=f"Found {replies_found} new replies"
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error syncing replies: {str(e)}")
