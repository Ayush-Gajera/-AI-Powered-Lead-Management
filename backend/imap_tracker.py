"""
IMAP reply tracking module
Scans inbox for replies and matches them with outbound emails
"""
import imaplib
import email
import os
from email.header import decode_header
from datetime import datetime
from typing import List, Dict, Optional
from dotenv import load_dotenv
import re

load_dotenv()

# IMAP Configuration
IMAP_HOST = os.getenv("IMAP_HOST", "imap.gmail.com")
IMAP_PORT = int(os.getenv("IMAP_PORT", "993"))
IMAP_USER = os.getenv("IMAP_USER")
IMAP_PASS = os.getenv("IMAP_PASS")
IMAP_MAILBOX = os.getenv("IMAP_MAILBOX", "INBOX")


def decode_mime_header(header_value: str) -> str:
    """Decode MIME encoded email headers"""
    if not header_value:
        return ""
    
    decoded_parts = decode_header(header_value)
    decoded_string = ""
    
    for part, encoding in decoded_parts:
        if isinstance(part, bytes):
            decoded_string += part.decode(encoding or 'utf-8', errors='ignore')
        else:
            decoded_string += part
    
    return decoded_string


def extract_plain_text(msg: email.message.Message) -> str:
    """Extract plain text from email message"""
    body = ""
    
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            content_disposition = str(part.get("Content-Disposition", ""))
            
            # Skip attachments
            if "attachment" in content_disposition:
                continue
            
            # Get plain text
            if content_type == "text/plain":
                try:
                    body = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                    break
                except:
                    pass
            # Fallback to HTML if no plain text
            elif content_type == "text/html" and not body:
                try:
                    html_body = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                    # Simple HTML tag removal
                    body = re.sub(r'<[^>]+>', '', html_body)
                except:
                    pass
    else:
        try:
            body = msg.get_payload(decode=True).decode('utf-8', errors='ignore')
        except:
            body = str(msg.get_payload())
    
    # Return first 500 characters as preview
    return body.strip()[:500]


def extract_message_ids(header_value: str) -> List[str]:
    """
    Extract message IDs from In-Reply-To or References header
    Returns list of message IDs without angle brackets
    """
    if not header_value:
        return []
    
    # Find all message IDs in angle brackets
    message_ids = re.findall(r'<([^>]+)>', header_value)
    return message_ids


def scan_inbox_for_replies(outbound_message_ids: List[str]) -> List[Dict]:
    """
    Scan inbox for replies matching outbound message IDs
    
    Args:
        outbound_message_ids: List of message IDs from sent emails
    
    Returns:
        List of reply dictionaries with matched information
    """
    replies = []
    
    try:
        # Connect to IMAP server
        mail = imaplib.IMAP4_SSL(IMAP_HOST, IMAP_PORT)
        mail.login(IMAP_USER, IMAP_PASS)
        mail.select(IMAP_MAILBOX)
        
        # Search for all emails (we'll check last 50 to avoid overwhelming)
        status, messages = mail.search(None, 'ALL')
        
        if status != 'OK':
            return replies
        
        # Get message IDs (last 50 emails)
        message_ids = messages[0].split()
        message_ids = message_ids[-50:] if len(message_ids) > 50 else message_ids
        
        # Process each email
        for msg_id in message_ids:
            try:
                # Fetch email
                status, msg_data = mail.fetch(msg_id, '(RFC822)')
                
                if status != 'OK':
                    continue
                
                # Parse email
                raw_email = msg_data[0][1]
                msg = email.message_from_bytes(raw_email)
                
                # Extract headers
                in_reply_to = msg.get('In-Reply-To', '')
                references = msg.get('References', '')
                from_email = msg.get('From', '')
                subject = decode_mime_header(msg.get('Subject', ''))
                date_str = msg.get('Date', '')
                
                # Extract message IDs from headers
                reply_to_ids = extract_message_ids(in_reply_to)
                reference_ids = extract_message_ids(references)
                
                # Combine all potential parent message IDs
                all_parent_ids = reply_to_ids + reference_ids
                
                # Check if any parent ID matches our outbound emails
                matched_message_id = None
                for parent_id in all_parent_ids:
                    if parent_id in outbound_message_ids:
                        matched_message_id = parent_id
                        break
                
                if matched_message_id:
                    # Extract email address from From header
                    from_email_clean = re.search(r'[\w\.-]+@[\w\.-]+', from_email)
                    from_email_clean = from_email_clean.group(0) if from_email_clean else from_email
                    
                    # Extract body preview
                    body_preview = extract_plain_text(msg)
                    
                    # Parse received date
                    try:
                        received_at = email.utils.parsedate_to_datetime(date_str)
                    except:
                        received_at = datetime.now()
                    
                    replies.append({
                        'matched_message_id': matched_message_id,
                        'from_email': from_email_clean,
                        'subject': subject,
                        'body_preview': body_preview,
                        'received_at': received_at.isoformat()
                    })
            
            except Exception as e:
                # Skip problematic emails
                continue
        
        # Close connection
        mail.close()
        mail.logout()
    
    except Exception as e:
        raise Exception(f"Failed to scan inbox: {str(e)}")
    
    return replies
