#!/bin/bash
# Deploy PL Content Bot to VPS

VPS="root@89.117.36.82"
REMOTE_DIR="/root/tyler"

echo "=== Deploying to $VPS ==="

# Create remote directory
ssh $VPS "mkdir -p $REMOTE_DIR"

# Sync files (excluding venv, logs, cache)
rsync -avz --progress \
    --exclude 'venv/' \
    --exclude '__pycache__/' \
    --exclude '*.pyc' \
    --exclude '.DS_Store' \
    --exclude 'logs/' \
    --exclude '.claude/' \
    /Users/elizavetapirozkova/Desktop/tyler/ \
    $VPS:$REMOTE_DIR/

echo ""
echo "=== Files synced! ==="
echo ""
echo "Now run on VPS:"
echo "  ssh $VPS"
echo "  cd $REMOTE_DIR"
echo "  chmod +x setup_vps.sh && ./setup_vps.sh"