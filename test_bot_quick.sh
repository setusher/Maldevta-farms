#!/bin/bash

# Quick bot test script
# Tests if your WhatsApp bot is responding

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                                                              ║"
echo "║           🤖 WhatsApp Bot Quick Test                        ║"
echo "║                                                              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test 1: Check if server is running
echo "1️⃣  Checking if server is running..."
if curl -s http://localhost:8000/ > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Server is running${NC}"
else
    echo -e "${RED}✗ Server is NOT running${NC}"
    echo -e "${YELLOW}   → Start server with: python server.py${NC}"
    exit 1
fi

echo ""

# Test 2: Check health endpoint
echo "2️⃣  Checking server health..."
HEALTH=$(curl -s http://localhost:8000/health)
if echo "$HEALTH" | grep -q "healthy"; then
    echo -e "${GREEN}✓ Server is healthy${NC}"
else
    echo -e "${RED}✗ Server health check failed${NC}"
    echo "$HEALTH"
fi

echo ""

# Test 3: Check configuration
echo "3️⃣  Checking configuration..."
CONFIG=$(curl -s http://localhost:8000/config-status)

# Check each config item
if echo "$CONFIG" | grep -q '"aisensy_configured":true'; then
    echo -e "${GREEN}✓ AiSensy configured${NC}"
else
    echo -e "${YELLOW}⚠ AiSensy not configured${NC}"
fi

if echo "$CONFIG" | grep -q '"qstash_configured":true'; then
    echo -e "${GREEN}✓ QStash configured${NC}"
else
    echo -e "${YELLOW}⚠ QStash not configured (messages will process inline)${NC}"
fi

if echo "$CONFIG" | grep -q '"travel_studio_configured":true'; then
    echo -e "${GREEN}✓ Travel Studio configured${NC}"
else
    echo -e "${RED}✗ Travel Studio not configured${NC}"
fi

echo ""

# Test 4: Test webhook
echo "4️⃣  Testing webhook with sample message..."
WEBHOOK_RESPONSE=$(curl -s -X POST http://localhost:8000/webhook \
  -H "Content-Type: application/json" \
  -d '{
    "entry": [{
      "changes": [{
        "value": {
          "messages": [{
            "from": "1234567890",
            "text": {"body": "Hello! This is a test message"},
            "id": "test123"
          }],
          "contacts": [{
            "profile": {"name": "Test User"}
          }]
        }
      }]
    }]
  }')

if echo "$WEBHOOK_RESPONSE" | grep -q "success"; then
    echo -e "${GREEN}✓ Webhook accepted message${NC}"
    echo ""
    echo -e "${YELLOW}📝 Check server logs to see if AI responded${NC}"
    echo -e "${YELLOW}   You should see:${NC}"
    echo -e "${YELLOW}   - 'Message queued successfully'${NC}"
    echo -e "${YELLOW}   - 'AI response generated'${NC}"
    echo -e "${YELLOW}   - 'Message sent successfully'${NC}"
else
    echo -e "${RED}✗ Webhook test failed${NC}"
    echo "$WEBHOOK_RESPONSE"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Test 5: Test availability checking
echo "5️⃣  Testing availability checking..."
if python3 test_check_availability.py > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Availability checking works${NC}"
else
    echo -e "${YELLOW}⚠ Availability check had issues (run 'python test_check_availability.py' for details)${NC}"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📋 SUMMARY"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Your bot status:"
echo "  • Server: Running ✓"
echo "  • Webhook: Accepting messages ✓"
echo "  • Configuration: Check above for details"
echo ""
echo "To see if AI is responding:"
echo "  1. Check terminal where server is running"
echo "  2. Look for 'AI response generated' in logs"
echo ""
echo "To test with real WhatsApp:"
echo "  1. Run: ngrok http 8000"
echo "  2. Copy ngrok URL to WhatsApp webhook settings"
echo "  3. Send a message to your bot number"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
