#!/bin/bash

# Quick OAuth Setup Script for Redis Memory Server
# This script helps you quickly set up and test OAuth authentication

set -e

echo "🔮 Redis Memory Server - OAuth Quick Setup"
echo "=========================================="

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
    read -p "Press Enter after you've updated .env..."
else
    echo "✅ .env file already exists"
fi

# Check if Redis is running
echo "🔍 Checking Redis connection..."
if redis-cli ping > /dev/null 2>&1; then
    echo "✅ Redis is running"
else
    echo "❌ Redis is not running. Starting Redis with Docker..."
    if command -v docker > /dev/null 2>&1; then
        docker run -d -p 6379:6379 --name redis-memory-test redis/redis-stack-server:latest
        echo "✅ Started Redis container"
        sleep 2
    else
        echo "❌ Docker not found. Please start Redis manually:"
        echo "   brew install redis && brew services start redis"
        echo "   OR"
        echo "   docker run -d -p 6379:6379 redis/redis-stack-server:latest"
        exit 1
    fi
fi

# Check environment variables
echo "🔍 Checking OAuth configuration..."
source .env

if [ -z "$OAUTH2_ISSUER_URL" ] || [ "$OAUTH2_ISSUER_URL" = "https://your-domain.auth0.com/" ]; then
    echo "❌ OAUTH2_ISSUER_URL not configured in .env"
    exit 1
fi

if [ -z "$OAUTH2_AUDIENCE" ] || [ "$OAUTH2_AUDIENCE" = "https://api.your-app.com" ]; then
    echo "❌ OAUTH2_AUDIENCE not configured in .env"
    exit 1
fi

if [ -z "$OAUTH_CLIENT_ID" ] || [ "$OAUTH_CLIENT_ID" = "your-client-id" ]; then
    echo "❌ OAUTH_CLIENT_ID not configured in .env"
    exit 1
fi

if [ -z "$OAUTH_CLIENT_SECRET" ] || [ "$OAUTH_CLIENT_SECRET" = "your-client-secret" ]; then
    echo "❌ OAUTH_CLIENT_SECRET not configured in .env"
    exit 1
fi

echo "✅ OAuth configuration looks good"

# Test OAuth token endpoint
echo "🔍 Testing OAuth token endpoint..."
OAUTH_DOMAIN=$(echo $OAUTH2_ISSUER_URL | sed 's|https://||' | sed 's|/||')

TOKEN_RESPONSE=$(curl -s -X POST "https://$OAUTH_DOMAIN/oauth/token" \
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

echo ""
echo "🚀 Setup complete! You can now:"
echo ""
echo "1. Start the memory server:"
echo "   uv run python -m agent_memory_server.main"
echo ""
echo "2. Run the automated OAuth test:"
echo "   uv run python manual_oauth_qa/manual_oauth_test.py"
echo ""
echo "3. Or follow the manual testing guide:"
echo "   cat manual_oauth_qa/README.md"
echo ""
echo " Happy testing!"
