import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = "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"
if not API_KEY:
    raise ValueError("Missing OPENROUTER_API_KEY in .env")

BASE_URL = "https://openrouter.ai/api/v1"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
    # Optional but recommended by OpenRouter:
    "HTTP-Referer": "http://localhost",
    "X-Title": "Lead Email Tool"
}

# ----------------------------
# 1) List available models
# ----------------------------
print("📌 Fetching available models from OpenRouter...")
models_res = requests.get(f"{BASE_URL}/models", headers=headers, timeout=30)
print("Status:", models_res.status_code)

if models_res.status_code != 200:
    print("❌ Failed to fetch models:", models_res.text)
    exit()

models_data = models_res.json()
models = models_data.get("data", [])

print(f"✅ Total models available: {len(models)}")
print("\nTop 10 models:")
for m in models[:10]:
    print("-", m.get("id"))

# ----------------------------
# 2) Test chat completion
# ----------------------------
test_model = "openai/gpt-4o-mini"  # Recommended for your project

payload = {
    "model": test_model,
    "messages": [
        {"role": "system", "content": "You are a helpful assistant. Reply only in JSON."},
        {"role": "user", "content": "Return JSON: {\"ok\": true, \"model\": \"<model_name>\"}"}
    ],
    "temperature": 0.2
}

print(f"\n📌 Testing model: {test_model}")
chat_res = requests.post(
    f"{BASE_URL}/chat/completions",
    headers=headers,
    json=payload,
    timeout=60
)

print("Status:", chat_res.status_code)

if chat_res.status_code != 200:
    print("❌ Chat completion failed:", chat_res.text)
    exit()

data = chat_res.json()
content = data["choices"][0]["message"]["content"]
print("\n✅ Response content:\n", content)
