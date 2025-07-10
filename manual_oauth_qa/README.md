# Manual OAuth QA Testing Guide

This folder contains everything needed to manually test OAuth authentication with the Redis Memory Server on any machine. The instructions assume you are running inside **Warp Terminal** so you can quickly execute the commands.

## 📋 Prerequisites

1. **OAuth Provider Account**: Create a client with any OAuth 2.0 provider
2. **Redis Server**: Running locally or accessible
3. **API Keys**: OpenAI and/or Anthropic API keys
4. **Python Environment**: With all dependencies installed

## 🚀 Quick Start

### Step 1: Set Up Your OAuth Provider

#### 1.1 Create an Application

1. Open your provider's dashboard
2. Create a **Machine to Machine** or equivalent application
3. Name it `Redis Memory Server API`

#### 1.2 Create API or Resource (if needed)

1. Create an API or resource server
2. Identifier: `https://api.redis-memory-server.com` (your audience)
3. Signing Algorithm: `RS256`

#### 1.3 Authorize Your Application

1. Allow the application to access the API
2. Select any required scopes

#### 1.4 Get Credentials

From your provider's dashboard, note down:

- **Domain**: e.g. `your-oauth-provider.com`
- **Client ID**: Found in application settings
- **Client Secret**: Found in application settings
- **Audience**: Your API identifier

### Step 2: Configure Environment

#### 2.1 Create .env File

Copy the `env_template` to `.env` and update with your values:

```bash
cp manual_oauth_qa/env_template .env
```

#### 2.2 Update .env with Your OAuth Values

```bash
# Authentication Configuration
DISABLE_AUTH=false
OAUTH2_ISSUER_URL=https://your-oauth-provider.com/
OAUTH2_AUDIENCE=https://api.redis-memory-server.com
OAUTH2_ALGORITHMS=["RS256"]

# OAuth Client Credentials (for testing script)
OAUTH_CLIENT_ID=your-client-id
OAUTH_CLIENT_SECRET=your-client-secret

# Your API Keys
OPENAI_API_KEY=your-actual-openai-key
ANTHROPIC_API_KEY=your-actual-anthropic-key
```

### Step 3: Start Services

#### 3.1 Start Redis

```bash
# Using Docker Compose
docker-compose up redis

# Or using Docker directly
docker run -d -p 6379:6379 redis/redis-stack-server:latest
```

#### 3.2 Start Memory Server

```bash
# Make sure authentication is enabled
export DISABLE_AUTH=false

# Start the server
uv run python -m agent_memory_server.main
```

You should see logs indicating:

- ✅ OAuth2 authentication configured
- ✅ Server starting on port 8000

### Step 4: Run Tests

#### Quick Automated Testing

```bash
# Run the comprehensive test script
uv run python manual_oauth_qa/test_oauth.py
```

This will:

1. Get an OAuth access token
2. Test all authenticated endpoints
3. Verify authentication rejection works
4. Provide a detailed report

## 📁 Files in This Folder

- **`README.md`** - This comprehensive guide
- **`env_template`** - Environment variable template
- **`test_oauth.py`** - Comprehensive OAuth test script
- **`setup_check.py`** - Pre-flight checks for dependencies
- **`debug_oauth.py`** - Debug script for troubleshooting
- **`quick_oauth_setup.sh`** - Automated setup script
- **`TROUBLESHOOTING.md`** - Detailed troubleshooting guide

## 🧪 Manual Testing Methods

### Method 1: Using the Automated Test Script

```bash
# Run the comprehensive test script
uv run python manual_oauth_qa/test_oauth.py
```

### Method 2: Manual cURL Testing

#### Get OAuth Token

```bash
# Set your OAuth credentials
export OAUTH_DOMAIN="your-oauth-provider.com"
export OAUTH_CLIENT_ID="your-client-id"
export OAUTH_CLIENT_SECRET="your-client-secret"
export OAUTH_AUDIENCE="https://api.redis-memory-server.com"

# Get access token
TOKEN=$(curl -s -X POST "https://$OAUTH_DOMAIN/oauth/token" \
  -H "Content-Type: application/json" \
  -d '{
    "client_id": "'$OAUTH_CLIENT_ID'",
    "client_secret": "'$OAUTH_CLIENT_SECRET'",
    "audience": "'$OAUTH_AUDIENCE'",
    "grant_type": "client_credentials"
  }' | jq -r '.access_token')

echo "Access Token: $TOKEN"
```

#### Test Endpoints with Token

```bash
# Test sessions endpoint
curl -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json" \
     http://localhost:8000/v1/working-memory/

# Test memory prompt
curl -X POST \
     -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"query": "What is the capital of France?", "session_id": "test-session"}' \
     http://localhost:8000/v1/memory/prompt

# Test long-term memory creation
curl -X POST \
     -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
       "memories": [
         {
          "text": "OAuth test memory",
           "session_id": "test-session",
           "namespace": "test"
         }
       ]
     }' \
     http://localhost:8000/v1/long-term-memory/

# Test memory search
curl -X POST \
     -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"text": "OAuth test", "limit": 5}' \
     http://localhost:8000/v1/long-term-memory/search
```

#### Test Authentication Rejection

```bash
# Test without token (should return 401)
curl -H "Content-Type: application/json" \
     http://localhost:8000/v1/working-memory/

# Test with invalid token (should return 401)
curl -H "Authorization: Bearer invalid.jwt.token" \
     -H "Content-Type: application/json" \
     http://localhost:8000/v1/working-memory/
```

### Method 3: Using Python Requests

```python
import requests
import json

# Get OAuth token
def get_oauth_token():
    token_url = "https://your-oauth-provider.com/oauth/token"
    payload = {
        "client_id": "your-client-id",
        "client_secret": "your-client-secret",
        "audience": "https://api.redis-memory-server.com",
        "grant_type": "client_credentials"
    }

    response = requests.post(token_url, json=payload)
    response.raise_for_status()
    return response.json()["access_token"]

# Test authenticated endpoint
token = get_oauth_token()
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

response = requests.get("http://localhost:8000/v1/working-memory/", headers=headers)
print(f"Status: {response.status_code}")
print(f"Response: {response.json()}")
```

## ✅ Verification Checklist

### Expected Behaviors

- [ ] **Health endpoint works without auth**: `GET /v1/health` returns 200
- [ ] **Authenticated endpoints require token**: Return 401 without `Authorization` header
- [ ] **Invalid tokens rejected**: Return 401 with malformed or expired tokens
- [ ] **Valid tokens accepted**: Return 200/201 with proper JWT tokens
- [ ] **JWKS validation works**: Server fetches and caches provider public keys
- [ ] **Token claims extracted**: User info extracted from JWT payload

### Provider-Specific Validations

- [ ] **Issuer validation**: Token `iss` claim matches `OAUTH2_ISSUER_URL`
- [ ] **Audience validation**: Token `aud` claim matches `OAUTH2_AUDIENCE`
- [ ] **Signature validation**: Token signature verified using provider JWKS
- [ ] **Expiration validation**: Expired tokens rejected
- [ ] **Algorithm validation**: Only RS256 tokens accepted

## 📊 Expected Test Results

When everything is working correctly, you should see:

```
🎉 All OAuth authentication tests passed!
📊 Test Summary
Authenticated endpoints: 4/4 passed
Health endpoint: ✅
No auth rejection: ✅
Invalid token rejection: ✅
```

## 🔧 Troubleshooting

### Common Issues

#### "OAuth2 issuer URL not configured"

- Check `OAUTH2_ISSUER_URL` in `.env`
- Ensure it ends with `/` (e.g., `https://your-domain.auth0.com/`)

#### "Unable to fetch JWKS"

- Check internet connectivity
- Verify provider domain is correct
- Check if the OAuth service is accessible

#### "Invalid audience"

- Verify `OAUTH2_AUDIENCE` matches your API identifier
- Check your application is authorized for the API

#### "Unable to find matching public key"

- Token `kid` doesn't match any key in provider JWKS
- Try regenerating the token
- Check provider key rotation settings

#### "Token has expired"

- Provider tokens have limited lifetime (usually 24 hours)
- Get a fresh token from your provider

#### Environment Variables Not Loading

- Check if shell environment is overriding .env: `env | grep OAUTH2`
- If found, unset conflicting variables: `unset OAUTH2_AUDIENCE`
- Restart your shell or reload .env: `source .env`

### Debug Steps

1. **Check configuration**: `python debug_oauth.py`
2. **Verify dependencies**: `python setup_check.py`
3. **Test the OAuth flow directly**: Use the cURL commands above
4. **Check server logs**: Look for authentication configuration messages

#### Debug Mode

Enable debug logging to see detailed authentication flow:

```bash
export LOG_LEVEL=DEBUG
uv run python -m agent_memory_server.main
```

This will show:

- JWKS fetching and caching
- JWT validation steps
- Authentication decisions

## 🔒 Security Notes

- Never commit your `.env` file to version control
- Use different OAuth applications for development and production
- Rotate client secrets regularly
- Monitor authentication logs for suspicious activity

### Production Considerations

#### Security Checklist

- [ ] **HTTPS Only**: Use HTTPS in production
- [ ] **Token Refresh**: Implement token refresh in clients
- [ ] **Rate Limiting**: Consider rate limiting on the token endpoint
- [ ] **Monitoring**: Monitor authentication failures
- [ ] **Key Rotation**: Handle provider key rotation gracefully

#### Performance Considerations

- [ ] **JWKS Caching**: Verify JWKS keys are cached (default 1 hour)
- [ ] **Connection Pooling**: Use connection pooling for provider requests
- [ ] **Token Validation**: JWT validation is CPU-intensive, consider caching

## 📞 Support

If you encounter issues:

1. Check the troubleshooting section above
2. Run the debug script: `python debug_oauth.py`
3. Verify your provider configuration in the dashboard
4. Check that all environment variables are set correctly
5. See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for detailed debugging

### Support Resources

- [OAuth 2.0 Spec](https://oauth.net/2/)
- [JWT.io](https://jwt.io/) - For debugging JWT tokens

---

This guide provides comprehensive manual testing for generic OAuth authentication. The automated test script (`test_oauth.py`) is the quickest way to verify everything works, while manual cURL/Python testing gives you more control and understanding of the authentication flow.
