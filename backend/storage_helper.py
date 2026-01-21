"""
Supabase Storage Helper for file uploads
Handles attachment storage in Supabase Storage bucket
"""
import os
from typing import Dict, Optional
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

# Supabase configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Storage bucket name
BUCKET_NAME = "email_attachments"


def upload_file_to_storage(
    file_bytes: bytes,
    file_name: str,
    content_type: str
) -> Dict:
    """
    Upload file to Supabase Storage
    
    Args:
        file_bytes: File content as bytes
        file_name: Name of the file
        content_type: MIME type
    
    Returns:
        Dict with file metadata including URL
    
    Raises:
        Exception if upload fails
    """
    try:
        # Generate unique file path (timestamp + original name)
        import time
        timestamp = int(time.time() * 1000)
        file_path = f"{timestamp}_{file_name}"
        
        print(f"📤 Uploading file to storage...")
        print(f"   File: {file_name}")
        print(f"   Size: {len(file_bytes)} bytes")
        print(f"   Type: {content_type}")
        print(f"   Path: {file_path}")
        
        # Upload to Supabase Storage
        response = supabase.storage.from_(BUCKET_NAME).upload(
            path=file_path,
            file=file_bytes,
            file_options={"content-type": content_type}
        )
        
        print(f"   ✅ Upload successful")
        
        # Get public URL
        public_url = supabase.storage.from_(BUCKET_NAME).get_public_url(file_path)
        print(f"   URL: {public_url}")
        
        return {
            "file_name": file_name,
            "file_url": public_url,
            "mime_type": content_type,
            "size": len(file_bytes),
            "storage_path": file_path
        }
    
    except Exception as e:
        print(f"   ❌ Upload failed: {str(e)}")
        import traceback
        traceback.print_exc()
        raise Exception(f"Failed to upload file to storage: {str(e)}")


def download_file_from_storage(file_url: str) -> bytes:
    """
    Download file from Supabase Storage URL
    
    Args:
        file_url: Public URL of the file
    
    Returns:
        File content as bytes
    """
    try:
        print(f"        🔽 Downloading from storage...")
        print(f"           URL: {file_url}")
        
        # Extract path from URL
        # URL format: https://{project}.supabase.co/storage/v1/object/public/email_attachments/{path}
        if "/object/public/" in file_url:
            parts = file_url.split("/object/public/")
            if len(parts) == 2:
                bucket_and_path = parts[1].split("/", 1)
                if len(bucket_and_path) == 2:
                    file_path = bucket_and_path[1]
                    print(f"           Extracted path: {file_path}")
                else:
                    raise ValueError("Invalid storage URL format")
            else:
                raise ValueError("Invalid storage URL format")
        else:
            raise ValueError("Not a Supabase storage URL")
        
        # Download file
        print(f"           Downloading from bucket: {BUCKET_NAME}")
        response = supabase.storage.from_(BUCKET_NAME).download(file_path)
        print(f"           ✅ Downloaded: {len(response)} bytes")
        return response
    
    except Exception as e:
        # Fallback: try downloading via HTTP
        print(f"           ⚠️ Supabase download failed: {str(e)}")
        print(f"           Trying HTTP fallback...")
        import httpx
        try:
            http_response = httpx.get(file_url, timeout=30)
            http_response.raise_for_status()
            print(f"           ✅ HTTP download successful: {len(http_response.content)} bytes")
            return http_response.content
        except Exception as http_error:
            print(f"           ❌ HTTP fallback also failed: {str(http_error)}")
            raise Exception(f"Failed to download file: {str(e)}, HTTP fallback: {str(http_error)}")


def delete_file_from_storage(file_path: str) -> None:
    """
    Delete file from Supabase Storage
    
    Args:
        file_path: Storage path of the file
    """
    try:
        supabase.storage.from_(BUCKET_NAME).remove([file_path])
    except Exception as e:
        print(f"Warning: Failed to delete file {file_path}: {str(e)}")


def ensure_bucket_exists() -> bool:
    """
    Check if storage bucket exists, create if not
    
    Returns:
        True if bucket exists or was created
    """
    try:
        # Try to list files (this will fail if bucket doesn't exist)
        buckets = supabase.storage.list_buckets()
        bucket_names = [b.name for b in buckets]
        
        if BUCKET_NAME not in bucket_names:
            # Create bucket
            supabase.storage.create_bucket(
                BUCKET_NAME,
                options={"public": False}  # Use signed URLs
            )
            print(f"✓ Created storage bucket: {BUCKET_NAME}")
        
        return True
    
    except Exception as e:
        print(f"Warning: Could not verify/create bucket: {str(e)}")
        print(f"Please create bucket '{BUCKET_NAME}' manually in Supabase Dashboard")
        return False
