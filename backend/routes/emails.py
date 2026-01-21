"""
API routes for email management
"""
from fastapi import APIRouter, HTTPException
from typing import List
from datetime import datetime
from models import SendEmailRequest, OutboundEmailResponse
from db import supabase
from email_sender import send_email

router = APIRouter(prefix="/emails", tags=["emails"])


@router.post("/send")
async def send_email_to_lead(request: SendEmailRequest):
    """Send email to a lead"""
    try:
        # Get lead details
        lead_response = supabase.table("leads").select("*").eq("id", request.lead_id).execute()
        
        if not lead_response.data:
            raise HTTPException(status_code=404, detail="Lead not found")
        
        lead = lead_response.data[0]
        
        # Send email via SMTP
        message_id = send_email(
            to_email=lead['email'],
            subject=request.subject,
            body=request.body
        )
        
        # Store outbound email in database
        current_time = datetime.now().isoformat()
        
        email_response = supabase.table("outbound_emails").insert({
            "lead_id": request.lead_id,
            "subject": request.subject,
            "body": request.body,
            "message_id": message_id,
            "sent_at": current_time
        }).execute()
        
        if not email_response.data:
            raise HTTPException(status_code=400, detail="Failed to store email")
        
        # Update lead status to EMAILED
        supabase.table("leads").update({
            "status": "EMAILED",
            "last_emailed_at": current_time
        }).eq("id", request.lead_id).execute()
        
        return {
            "success": True,
            "message": f"Email sent to {lead['email']}",
            "email_id": email_response.data[0]['id'],
            "message_id": message_id
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error sending email: {str(e)}")


@router.get("/outbound", response_model=List[OutboundEmailResponse])
async def list_outbound_emails():
    """List all outbound emails"""
    try:
        response = supabase.table("outbound_emails").select("*").order("sent_at", desc=True).execute()
        return response.data
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching emails: {str(e)}")
