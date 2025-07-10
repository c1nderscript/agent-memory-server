#!/usr/bin/env python3
import os

import httpx
from dotenv import load_dotenv


load_dotenv()

OAUTH_DOMAIN = (
    os.getenv("OAUTH2_ISSUER_URL", "").replace("https://", "").replace("/", "")
)
OAUTH_CLIENT_ID = os.getenv("OAUTH_CLIENT_ID")
OAUTH_CLIENT_SECRET = os.getenv("OAUTH_CLIENT_SECRET")
OAUTH_AUDIENCE = os.getenv("OAUTH2_AUDIENCE")

print("=== OAuth Configuration Debug ===")
print(f"Domain: {OAUTH_DOMAIN}")
print(f"Client ID: {OAUTH_CLIENT_ID}")
print(
    f"Client Secret: {OAUTH_CLIENT_SECRET[:10]}..." if OAUTH_CLIENT_SECRET else "None"
)
print(f"Audience: {OAUTH_AUDIENCE}")
print(f"Token URL: https://{OAUTH_DOMAIN}/oauth/token")

print("\n=== Validation ===")
missing = []
if not OAUTH_DOMAIN:
    missing.append("OAUTH2_ISSUER_URL")
if not OAUTH_CLIENT_ID:
    missing.append("OAUTH_CLIENT_ID")
if not OAUTH_CLIENT_SECRET:
    missing.append("OAUTH_CLIENT_SECRET")
if not OAUTH_AUDIENCE:
    missing.append("OAUTH2_AUDIENCE")

if missing:
    print(f"❌ Missing: {', '.join(missing)}")
    exit(1)
else:
    print("✅ All required values present")

print("\n=== Testing OAuth Token Request ===")
token_url = f"https://{OAUTH_DOMAIN}/oauth/token"
payload = {
    "client_id": OAUTH_CLIENT_ID,
    "client_secret": OAUTH_CLIENT_SECRET,
    "audience": OAUTH_AUDIENCE,
    "grant_type": "client_credentials",
}

print(f"Request URL: {token_url}")
print(f"Request payload: {payload}")

try:
    with httpx.Client(timeout=10.0) as client:
        response = client.post(
            token_url, json=payload, headers={"Content-Type": "application/json"}
        )
        print(f"Response status: {response.status_code}")
        print(f"Response: {response.text}")

        if response.status_code == 200:
            print("✅ OAuth token request successful!")
        else:
            print("❌ OAuth token request failed!")

except Exception as e:
    print(f"❌ Exception during token request: {e}")
