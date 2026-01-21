"""
Shared AI Provider module using OpenRouter API
Replaces direct Gemini integration
"""
import os
import json
import requests
import re
from dotenv import load_dotenv

load_dotenv()

# Configuration
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "openai/gpt-4o-mini")
BASE_URL = "https://openrouter.ai/api/v1"

if not OPENROUTER_API_KEY:
    print("⚠️ Warning: OPENROUTER_API_KEY is missing in .env")

def call_ai_model(prompt: str, system_message: str = None, json_mode: bool = True) -> str:
    """
    Call OpenRouter API with the given prompt
    
    Args:
        prompt: The user prompt
        system_message: Optional system instruction
        json_mode: Whether to enforce JSON response (adds 'Reply in JSON' instruction)
        
    Returns:
        The content string from the AI response
    """
    if not OPENROUTER_API_KEY:
        raise ValueError("OPENROUTER_API_KEY not configured")

    messages = []
    
    # Add system message
    full_system_msg = system_message or "You are a helpful AI assistant."
    if json_mode:
        full_system_msg += " You MUST reply with valid JSON only. Do not wrap in markdown code blocks."
    
    messages.append({"role": "system", "content": full_system_msg})
    messages.append({"role": "user", "content": prompt})

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost:3000",
        "X-Title": "Lead Email Tool"
    }
    
    payload = {
        "model": OPENROUTER_MODEL,
        "messages": messages,
        "temperature": 0.2, # Low temperature for consistent formatting
        "response_format": {"type": "json_object"} if json_mode else None
    }
    
    try:
        print(f"🤖 Calling OpenRouter ({OPENROUTER_MODEL})...")
        response = requests.post(
            f"{BASE_URL}/chat/completions",
            headers=headers,
            json=payload,
            timeout=60
        )
        
        if response.status_code != 200:
            error_msg = f"OpenRouter API Error: {response.status_code} - {response.text}"
            print(f"❌ {error_msg}")
            raise Exception(error_msg)
            
        data = response.json()
        content = data["choices"][0]["message"]["content"]
        
        # Clean markdown code blocks if present (some models still add them despite instructions)
        if json_mode:
            content = clean_json_string(content)
            
        return content
        
    except Exception as e:
        print(f"❌ AI Call Failed: {str(e)}")
        raise

def clean_json_string(text: str) -> str:
    """
    Remove markdown code blocks (```json ... ```) from string
    """
    # Remove ```json ... ``` or ``` ... ```
    text = re.sub(r'^```(?:json)?\s*', '', text, flags=re.MULTILINE)
    text = re.sub(r'\s*```$', '', text, flags=re.MULTILINE)
    return text.strip()
