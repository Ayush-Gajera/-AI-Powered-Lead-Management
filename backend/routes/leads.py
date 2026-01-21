"""
API routes for lead management
"""
from fastapi import APIRouter, HTTPException
from typing import List
from models import LeadCreate, LeadResponse
from db import supabase

router = APIRouter(prefix="/leads", tags=["leads"])


@router.post("", response_model=LeadResponse)
async def create_lead(lead: LeadCreate):
    """Create a new lead"""
    try:
        # Insert lead into database
        response = supabase.table("leads").insert({
            "name": lead.name,
            "email": lead.email,
            "company": lead.company,
            "status": "NEW"
        }).execute()
        
        if not response.data:
            raise HTTPException(status_code=400, detail="Failed to create lead")
        
        return response.data[0]
    
    except Exception as e:
        # Check for duplicate email
        if "duplicate key" in str(e).lower() or "unique" in str(e).lower():
            raise HTTPException(status_code=400, detail="Lead with this email already exists")
        raise HTTPException(status_code=500, detail=f"Error creating lead: {str(e)}")


@router.get("", response_model=List[LeadResponse])
async def list_leads():
    """List all leads"""
    try:
        response = supabase.table("leads").select("*").order("created_at", desc=True).execute()
        return response.data
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching leads: {str(e)}")
