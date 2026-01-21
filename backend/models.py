"""
Pydantic models for request/response validation
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime


class LeadCreate(BaseModel):
    name: str
    email: EmailStr
    company: Optional[str] = None


class LeadResponse(BaseModel):
    id: str
    name: str
    email: str
    company: Optional[str]
    status: str
    created_at: str
    last_emailed_at: Optional[str]
    last_replied_at: Optional[str]
    lead_score: int = 0
    lead_priority: str = "LOW"
    last_reply_score: Optional[int] = None
    last_reply_intent: Optional[str] = None


class SendEmailRequest(BaseModel):
    lead_id: str
    subject: str
    body: str


class OutboundEmailResponse(BaseModel):
    id: str
    lead_id: str
    subject: str
    body: str
    message_id: str
    sent_at: str
    is_replied: bool


class ReplyScoring(BaseModel):
    """AI scoring response model"""
    reply_score: int = Field(ge=0, le=100)
    priority: str = Field(pattern="^(HIGH|MEDIUM|LOW|IGNORE)$")
    intent: str
    confidence: float = Field(ge=0.0, le=1.0)
    reasons: List[str]


class InboundReplyResponse(BaseModel):
    id: str
    lead_id: str
    outbound_email_id: str
    from_email: str
    subject: Optional[str]
    body_preview: Optional[str]
    received_at: str
    reply_score: int = 0
    priority: str = "LOW"
    intent: Optional[str] = None
    confidence: Optional[float] = None
    reasons: Optional[List[str]] = None


class SyncRepliesResponse(BaseModel):
    success: bool
    replies_found: int
    message: str
