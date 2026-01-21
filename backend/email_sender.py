"""
SMTP email sender module
Sends emails and generates unique Message-ID for reply tracking
"""
import smtplib
import os
from email.message import EmailMessage
from email.utils import make_msgid
from dotenv import load_dotenv
from typing import List, Dict, Optional
import mimetypes

load_dotenv()

# SMTP Configuration
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASS = os.getenv("SMTP_PASS")
SMTP_FROM_EMAIL = os.getenv("SMTP_FROM_EMAIL")


def send_email(to_email: str, subject: str, body: str) -> str:
    """
    Send an email via SMTP and return the Message-ID
    
    Args:
        to_email: Recipient email address
        subject: Email subject
        body: Email body (plain text)
    
    Returns:
        message_id: Unique Message-ID for reply tracking
    
    Raises:
        Exception: If email sending fails
    """
    try:
        # Create email message
        msg = EmailMessage()
        msg['From'] = SMTP_FROM_EMAIL
        msg['To'] = to_email
        msg['Subject'] = subject
        
        # Generate unique Message-ID
        # Format: <unique-id@domain>
        message_id = make_msgid(domain=SMTP_FROM_EMAIL.split('@')[1])
        msg['Message-ID'] = message_id
        
        # Set body content
        msg.set_content(body)
        
        # Connect to SMTP server and send
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()  # Upgrade to secure connection
            server.login(SMTP_USER, SMTP_PASS)
            server.send_message(msg)
        
        # Return Message-ID without angle brackets for storage
        return message_id.strip('<>')
    
    except Exception as e:
        raise Exception(f"Failed to send email: {str(e)}")


def send_reply_email(
    to_email: str,
    subject: str,
    body: str,
    in_reply_to: str,
    references: Optional[str] = None,
    attachments: Optional[List[Dict]] = None
) -> str:
    """
    Send a reply email with proper threading headers and attachments
    
    Args:
        to_email: Recipient email address
        subject: Email subject
        body: Email body (plain text)
        in_reply_to: Message-ID of the email we're replying to
        references: Chain of Message-IDs (optional)
        attachments: List of attachment dicts with file_url, file_name, mime_type
    
    Returns:
        message_id: Unique Message-ID for this reply
    
    Raises:
        Exception: If email sending fails
    """
    try:
        # Create email message
        msg = EmailMessage()
        msg['From'] = SMTP_FROM_EMAIL
        msg['To'] = to_email
        msg['Subject'] = subject
        
        # Generate unique Message-ID
        message_id = make_msgid(domain=SMTP_FROM_EMAIL.split('@')[1])
        msg['Message-ID'] = message_id
        
        # Add threading headers
        # In-Reply-To: immediate parent message
        msg['In-Reply-To'] = f"<{in_reply_to}>"
        
        # References: chain of all parent messages
        if references:
            msg['References'] = f"<{references}> <{in_reply_to}>"
        else:
            msg['References'] = f"<{in_reply_to}>"
        
        # Set body content
        msg.set_content(body)
        
        # Add attachments if provided
        attachment_count = len(attachments) if attachments else 0
        print(f"📎 Processing {attachment_count} attachment(s)")
        
        if attachments and attachment_count > 0:
            from storage_helper import download_file_from_storage
            
            for idx, attachment in enumerate(attachments):
                try:
                    file_url = attachment.get('file_url')
                    file_name = attachment.get('file_name', 'attachment')
                    mime_type = attachment.get('mime_type', 'application/octet-stream')
                    
                    print(f"  [{idx+1}] Processing: {file_name}")
                    print(f"      URL: {file_url}")
                    print(f"      MIME: {mime_type}")
                    
                    if not file_url:
                        print(f"      ❌ Error: No file_url provided")
                        continue
                    
                    # Download file from storage
                    file_bytes = download_file_from_storage(file_url)
                    print(f"      Downloaded: {len(file_bytes)} bytes")
                    
                    # Parse MIME type
                    maintype, subtype = mime_type.split('/', 1) if '/' in mime_type else ('application', 'octet-stream')
                    
                    # Add attachment to message
                    msg.add_attachment(
                        file_bytes,
                        maintype=maintype,
                        subtype=subtype,
                        filename=file_name
                    )
                    print(f"      ✅ Successfully attached: {file_name}")
                    
                except Exception as e:
                    print(f"      ❌ Failed to attach {attachment.get('file_name', 'unknown')}: {str(e)}")
                    import traceback
                    print(f"      Traceback:")
                    traceback.print_exc()
                    # Continue with other attachments
        
        # Connect to SMTP server and send
        print(f"📧 Connecting to SMTP server...")
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
            server.send_message(msg)
        
        print(f"✅ Reply email sent successfully to {to_email} with {attachment_count} attachment(s)")
        
        # Return Message-ID without angle brackets
        return message_id.strip('<>')
    
    except Exception as e:
        print(f"❌ Failed to send reply email: {str(e)}")
        import traceback
        traceback.print_exc()
        raise Exception(f"Failed to send reply email: {str(e)}")
