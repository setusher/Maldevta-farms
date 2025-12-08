#!/bin/bash

# WhatsApp Bot Startup Script

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                                                              ║"
echo "║        🤖 Starting WhatsApp Reservation Agent...            ║"
echo "║                                                              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Check if we're in the right directory
if [ ! -f "server.py" ]; then
    echo "❌ Error: server.py not found"
    echo "   Please run this script from the gyde-ai-whatsapp directory"
    exit 1
fi

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚠️  Warning: .env file not found"
    echo "   Some features may not work without configuration"
    echo ""
fi

# Check if another server is running on port 8000
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "⚠️  Warning: Port 8000 is already in use"
    echo ""
    echo "Options:"
    echo "  1. Stop the other server"
    echo "  2. Use a different port (edit server.py)"
    echo ""
    read -p "Stop the server on port 8000? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        PID=$(lsof -Pi :8000 -sTCP:LISTEN -t)
        kill $PID 2>/dev/null
        echo "✓ Stopped server on port 8000"
        sleep 1
    else
        echo "❌ Cannot start - port 8000 is in use"
        exit 1
    fi
fi

echo "🚀 Starting WhatsApp bot..."
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "✓ Bot will run on: http://localhost:8000"
echo "✓ Press CTRL+C to stop"
echo ""
echo "To test the bot:"
echo "  1. Open another terminal"
echo "  2. Run: curl http://localhost:8000/"
echo "  3. Should see: WhatsApp Reservation Agent"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Start the bot
python3 server.py
