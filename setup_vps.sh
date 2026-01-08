#!/bin/bash
# Setup PL Content Bot on VPS (run this on VPS)

set -e

echo "=== Setting up PL Content Bot ==="

# Install Python if needed
if ! command -v python3 &> /dev/null; then
    echo "Installing Python..."
    apt update && apt install -y python3 python3-pip python3-venv git
fi

# Clone or update repo
cd /root
if [ -d "tyler" ]; then
    echo "Updating existing repo..."
    cd tyler
    git pull
else
    echo "Cloning repo..."
    git clone git@github.com:vilin1927/tyler_news.git tyler
    cd tyler
fi

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate and install dependencies
echo "Installing dependencies..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Create logs directory
mkdir -p logs

# Check for .env file
if [ ! -f ".env" ]; then
    echo ""
    echo "WARNING: .env file not found!"
    echo "Copy .env.example to .env and add your API keys:"
    echo "  cp .env.example .env"
    echo "  nano .env"
    echo ""
fi

# Check for credentials.json
if [ ! -f "credentials.json" ]; then
    echo ""
    echo "WARNING: credentials.json not found!"
    echo "Upload your Google service account credentials."
    echo ""
fi

# Create systemd service
echo "Creating systemd service..."
cat > /etc/systemd/system/tyler-bot.service << 'EOF'
[Unit]
Description=PL Content Bot (Tyler)
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/tyler
ExecStart=/root/tyler/venv/bin/python src/telegram_bot.py
Restart=always
RestartSec=10
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd and enable service
systemctl daemon-reload
systemctl enable tyler-bot

echo ""
echo "=== Setup complete! ==="
echo ""
echo "NEXT STEPS:"
echo "1. Create .env file:  cp .env.example .env && nano .env"
echo "2. Upload credentials.json for Google Sheets"
echo "3. Start bot:  systemctl start tyler-bot"
echo ""
echo "COMMANDS:"
echo "  systemctl start tyler-bot    # Start bot"
echo "  systemctl stop tyler-bot     # Stop bot"
echo "  systemctl restart tyler-bot  # Restart bot"
echo "  systemctl status tyler-bot   # Check status"
echo "  journalctl -u tyler-bot -f   # View logs"
echo ""
echo "UPDATE FROM GITHUB:"
echo "  cd /root/tyler && git pull && systemctl restart tyler-bot"
