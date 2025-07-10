#!/bin/bash

# Quick OAuth Setup Script for Redis Memory Server
# This script helps you quickly set up and test OAuth authentication

set -e

echo "🔮 Redis Memory Server - OAuth Quick Setup"
echo "=========================================="

# Check if we're in the right directory
if [ ! -f "pyproject.toml" ]; then
    echo "❌ Please run this script from the redis-memory-server root directory"
    exit 1
fi

# Check if .env exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp manual_oauth_qa/env_template .env
    echo "✅ Created .env file"
    echo ""
    echo "⚠️  IMPORTANT: Please edit .env and update the following values:"
    echo "   - OAUTH2_ISSUER_URL (issuer URL from your provider)"
    echo "   - OAUTH2_AUDIENCE (API identifier)"
    echo "   - OAUTH_CLIENT_ID (client ID)"
    echo "   - OAUTH_CLIENT_SECRET (client secret)"
    echo "   - OPENAI_API_KEY (your OpenAI API key)"
    echo "   - ANTHROPIC_API_KEY (your Anthropic API key)"
    echo ""
    echo "Then run this script again to continue setup."
    exit 0
else
    echo "✅ .env file already exists"
fi

# Check Redis connection
echo "🔍 Checking Redis connection..."
if redis-cli ping >/dev/null 2>&1; then
    echo "✅ Redis is running"
else
    echo "❌ Redis is not running. Please start Redis:"
    echo "   brew services start redis  # macOS with Homebrew"
    echo "   sudo systemctl start redis # Linux with systemd"
    echo "   redis-server               # Manual start"
    exit 1
fi

# Check OAuth configuration
echo "🔍 Checking OAuth configuration..."
source .env

if [[ -z "$OAUTH2_ISSUER_URL" || "$OAUTH2_ISSUER_URL" == "https://your-domain.auth0.com/" ]]; then
    echo "❌ OAUTH2_ISSUER_URL not configured in .env"
    exit 1
fi

if [[ -z "$OAUTH2_AUDIENCE" || "$OAUTH2_AUDIENCE" == "https://api.redis-memory-server.com" ]]; then
    echo "❌ OAUTH2_AUDIENCE not configured in .env"
    exit 1
fi

if [[ -z "$OAUTH_CLIENT_ID" || "$OAUTH_CLIENT_ID" == "your-client-id" ]]; then
    echo "❌ OAUTH_CLIENT_ID not configured in .env"
    exit 1
fi

if [[ -z "$OAUTH_CLIENT_SECRET" || "$OAUTH_CLIENT_SECRET" == "your-client-secret" ]]; then
    echo "❌ OAUTH_CLIENT_SECRET not configured in .env"
    exit 1
fi

echo "✅ OAuth configuration looks good"

# Test OAuth token endpoint
echo "🔍 Testing OAuth token endpoint..."
DOMAIN=$(echo $OAUTH2_ISSUER_URL | sed 's|https://||' | sed 's|/$||')
TOKEN_RESPONSE=$(curl -s -X POST "https://$DOMAIN/oauth/token" \
    -H "Content-Type: application/json" \
    -d "{
    \"client_id\": \"$OAUTH_CLIENT_ID\",
    \"client_secret\": \"$OAUTH_CLIENT_SECRET\",
    \"audience\": \"$OAUTH2_AUDIENCE\",
    \"grant_type\": \"client_credentials\"
  }")

if echo "$TOKEN_RESPONSE" | grep -q "access_token"; then
    echo "✅ Successfully obtained OAuth token"
else
    echo "❌ Failed to get OAuth token:"
    echo "$TOKEN_RESPONSE"
    exit 1
fi

# Check if memory server is running
echo "🔍 Checking memory server..."
PORT=${PORT:-8000}
if curl -s "http://localhost:$PORT/v1/health" >/dev/null 2>&1; then
    echo "✅ Memory server is running on port $PORT"

    echo ""
    echo "🚀 Setup complete! You can now:"
    echo ""
    echo "1. Run the comprehensive OAuth test:"
    echo "   python manual_oauth_qa/test_oauth.py"
    echo ""
    echo "2. Run setup checks:"
    echo "   python manual_oauth_qa/setup_check.py"
    echo ""
    echo "3. Debug OAuth configuration:"
    echo "   python manual_oauth_qa/debug_oauth.py"
    echo ""
    echo "🎉 Happy testing!"
else
    echo "❌ Memory server is not running on port $PORT"
    echo ""
    echo "Start the memory server with:"
    echo "   uv run python -m agent_memory_server.main"
    echo ""
    echo "Then run the OAuth tests:"
    echo "   python manual_oauth_qa/test_oauth.py"
fi
