"""
API routes for inbound replies management
Handles next action generation, draft replies, and sending
"""
from fastapi import APIRouter, HTTPException, UploadFile, File, Query
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel
from db import supabase
from ai_next_action import generate_next_action
from ai_draft_reply import generate_draft_reply
from email_sender import send_reply_email
from storage_helper import upload_file_to_storage

router = APIRouter(prefix="/replies", tags=["replies"])


# Pydantic Models
class NextActionResponse(BaseModel):
    next_action_title: str
    next_action_steps: List[str]
    urgency: str
    followup_days: int
    suggested_tone: str


class DraftReplyResponse(BaseModel):
    subject: str
    body: str
    tone: str
    cached: bool = False


class SendDraftRequest(BaseModel):
    edited_subject: Optional[str] = None
    edited_body: Optional[str] = None
    attachments: Optional[List[dict]] = None


class FileUploadResponse(BaseModel):
    file_name: str
    file_url: str
    mime_type: str
    size: int


@router.get("/inbound-replies")
async def list_inbound_replies():
    """
    List all inbound replies with full details including next actions and drafts
    """
    try:
        # Query with joins
        response = supabase.table("inbound_replies").select(
            """
            *,
            leads(*),
            outbound_emails(*)
            """
        ).order("received_at", desc=True).execute()
        
        return response.data
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching replies: {str(e)}")


@router.post("/{reply_id}/generate-next-action", response_model=NextActionResponse)
async def generate_next_action_endpoint(
    reply_id: str,
    force: bool = Query(False, description="Force regeneration if already exists")
):
    """
    Generate next best action for a reply
    Uses caching unless force=true
    """
    try:
        # Get reply details
        reply_response = supabase.table("inbound_replies").select("*").eq("id", reply_id).execute()
        
        if not reply_response.data:
            raise HTTPException(status_code=404, detail="Reply not found")
        
        reply = reply_response.data[0]
        
        # Check if already generated
        if reply.get('next_action_generated_at') and not force:
            return NextActionResponse(
                next_action_title=reply['next_action_title'],
                next_action_steps=reply['next_action_steps'],
                urgency=reply['urgency'],
                followup_days=reply['followup_days'],
                suggested_tone=reply['suggested_tone']
            )
        
        # Get lead details
        lead_response = supabase.table("leads").select("*").eq("id", reply['lead_id']).execute()
        lead = lead_response.data[0] if lead_response.data else {}
        
        # Get outbound email context
        outbound_response = supabase.table("outbound_emails").select("*").eq(
            "id", reply['outbound_email_id']
        ).execute()
        outbound = outbound_response.data[0] if outbound_response.data else {}
        
        # Generate next action
        action = generate_next_action(
            reply_text=reply.get('body_preview', ''),
            intent=reply.get('intent', 'OTHER'),
            score=reply.get('reply_score', 50),
            priority=reply.get('priority', 'MEDIUM'),
            lead_name=lead.get('name', 'Customer'),
            lead_company=lead.get('company'),
            outbound_subject=outbound.get('subject'),
            outbound_body=outbound.get('body')
        )
        
        # Store in database
        current_time = datetime.now().isoformat()
        
        supabase.table("inbound_replies").update({
            "next_action_title": action.next_action_title,
            "next_action_steps": action.next_action_steps,
            "urgency": action.urgency,
            "followup_days": action.followup_days,
            "suggested_tone": action.suggested_tone,
            "next_action_generated_at": current_time
        }).eq("id", reply_id).execute()
        
        # Also update lead table with latest action
        supabase.table("leads").update({
            "next_action_title": action.next_action_title,
            "next_action_steps": action.next_action_steps,
            "next_action_updated_at": current_time
        }).eq("id", reply['lead_id']).execute()
        
        return NextActionResponse(
            next_action_title=action.next_action_title,
            next_action_steps=action.next_action_steps,
            urgency=action.urgency,
            followup_days=action.followup_days,
            suggested_tone=action.suggested_tone
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating next action: {str(e)}")


@router.post("/{reply_id}/generate-draft", response_model=DraftReplyResponse)
async def generate_draft_endpoint(
    reply_id: str,
    tone: str = Query("FRIENDLY", regex="^(FORMAL|FRIENDLY|SHORT)$"),
    force: bool = Query(False, description="Force regeneration")
):
    """
    Generate draft reply email
    Uses caching if same tone and not forced
    """
    try:
        # Get reply details
        reply_response = supabase.table("inbound_replies").select("*").eq("id", reply_id).execute()
        
        if not reply_response.data:
            raise HTTPException(status_code=404, detail="Reply not found")
        
        reply = reply_response.data[0]
        
        # Check cache
        if (reply.get('draft_generated_at') and 
            reply.get('draft_tone') == tone and 
            not force):
            return DraftReplyResponse(
                subject=reply['draft_subject'],
                body=reply['draft_body'],
                tone=reply['draft_tone'],
                cached=True
            )
        
        # Get lead details
        lead_response = supabase.table("leads").select("*").eq("id", reply['lead_id']).execute()
        lead = lead_response.data[0] if lead_response.data else {}
        
        # Get outbound email for subject
        outbound_response = supabase.table("outbound_emails").select("*").eq(
            "id", reply['outbound_email_id']
        ).execute()
        outbound = outbound_response.data[0] if outbound_response.data else {}
        
        # Get next action steps for context
        next_action_steps = reply.get('next_action_steps', []) or []
        
        # Generate draft
        draft = generate_draft_reply(
            lead_name=lead.get('name', 'Customer'),
            lead_company=lead.get('company'),
            reply_text=reply.get('body_preview', ''),
            intent=reply.get('intent', 'OTHER'),
            next_action_steps=next_action_steps,
            tone=tone,
            attachments=reply.get('attachments', []),
            original_subject=outbound.get('subject')
        )
        
        # Store in database
        current_time = datetime.now().isoformat()
        
        supabase.table("inbound_replies").update({
            "draft_subject": draft.subject,
            "draft_body": draft.body,
            "draft_tone": tone,
            "draft_generated_at": current_time,
            "draft_status": "GENERATED"
        }).eq("id", reply_id).execute()
        
        return DraftReplyResponse(
            subject=draft.subject,
            body=draft.body,
            tone=tone,
            cached=False
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating draft: {str(e)}")


@router.post("/{reply_id}/send-draft")
async def send_draft_endpoint(reply_id: str, request: SendDraftRequest):
    """
    Send draft reply email with proper threading
    """
    try:
        # Get reply details
        reply_response = supabase.table("inbound_replies").select("*").eq("id", reply_id).execute()
        
        if not reply_response.data:
            raise HTTPException(status_code=404, detail="Reply not found")
        
        reply = reply_response.data[0]
        
        # Get lead details
        lead_response = supabase.table("leads").select("*").eq("id", reply['lead_id']).execute()
        if not lead_response.data:
            raise HTTPException(status_code=404, detail="Lead not found")
        lead = lead_response.data[0]
        
        # Get outbound email for threading
        outbound_response = supabase.table("outbound_emails").select("*").eq(
            "id", reply['outbound_email_id']
        ).execute()
        if not outbound_response.data:
            raise HTTPException(status_code=404, detail="Outbound email not found")
        outbound = outbound_response.data[0]
        
        # Determine subject and body (use edited or draft)
        subject = request.edited_subject or reply.get('draft_subject', 'Re: Your inquiry')
        body = request.edited_body or reply.get('draft_body', 'Thank you for your message.')
        attachments = request.attachments or reply.get('attachments', [])
        
        # Debug logging
        print(f"📧 Sending draft reply to {lead['email']}")
        print(f"  Subject: {subject}")
        print(f"  Attachments from request: {request.attachments}")
        print(f"  Attachments from DB: {reply.get('attachments', [])}")
        print(f"  Final attachments: {attachments}")
        
        # Send email with threading
        new_message_id = send_reply_email(
            to_email=lead['email'],
            subject=subject,
            body=body,
            in_reply_to=outbound['message_id'],
            references=outbound.get('thread_root_message_id', outbound['message_id']),
            attachments=attachments
        )
        
        # Store sent email in outbound_emails
        current_time = datetime.now().isoformat()
        
        sent_email = supabase.table("outbound_emails").insert({
            "lead_id": reply['lead_id'],
            "subject": subject,
            "body": body,
            "message_id": new_message_id,
            "sent_at": current_time,
            "email_type": "REPLY",
            "attachments": attachments,
            "thread_root_message_id": outbound.get('thread_root_message_id', outbound['message_id'])
        }).execute()
        
        # Update reply draft status
        draft_status = "EDITED_SENT" if request.edited_subject or request.edited_body else "SENT"
        
        supabase.table("inbound_replies").update({
            "draft_status": draft_status
        }).eq("id", reply_id).execute()
        
        return {
            "success": True,
            "message": f"Reply sent to {lead['email']}",
            "sent_email_id": sent_email.data[0]['id'] if sent_email.data else None,
            "message_id": new_message_id
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error sending draft: {str(e)}")


@router.post("/upload-attachment", response_model=FileUploadResponse)
async def upload_attachment(file: UploadFile = File(...)):
    """
    Upload file to Supabase Storage
    """
    try:
        # Read file content
        file_bytes = await file.read()
        
        # Upload to storage
        file_metadata = upload_file_to_storage(
            file_bytes=file_bytes,
            file_name=file.filename,
            content_type=file.content_type or "application/octet-stream"
        )
        
        return FileUploadResponse(**file_metadata)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading file: {str(e)}")
