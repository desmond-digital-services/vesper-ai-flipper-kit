#!/bin/bash
# RedWand - Deploy to DreamHost (with credentials)

# Configuration
source ~/clawdbot/skills/dreamhost-manager/.env

DREAMHOST_SERVER=$DREAMHOST_SERVER
DREAMHOST_USER=$DREAMHOST_USER
DREAMHOST_PATH=$DREAMHOST_PATH

echo "==================================="
echo "RedWand - Deploy to DreamHost"
echo "==================================="
echo ""

# Step 1: Create deployment package
echo "Step 1: Packaging web files..."
cd "$(dirname "$0")"
tar -czf redwand-ai-web.tar.gz --exclude='.DS_Store' web/

if [ $? -eq 0 ]; then
    echo "✓ Package created: redwand-ai-web.tar.gz"
else
    echo "✗ Package creation failed"
    exit 1
fi
echo ""

# Step 2: Upload to DreamHost
echo "Step 2: Uploading to DreamHost..."
sftp $DREAMHOST_USER@$DREAMHOST_SERVER <<EOF
cd $DREAMHOST_PATH
put redwand-ai-web.tar.gz
bye
EOF

if [ $? -eq 0 ]; then
    echo "✓ Upload successful"
else
    echo "✗ Upload failed - check credentials"
    echo ""
    echo "Credentials used:"
    echo "  Server: $DREAMHOST_SERVER"
    echo "  User: $DREAMHOST_USER"
    exit 1
fi
echo ""

# Step 3: Extract on server
echo "Step 3: Extracting files on server..."
ssh $DREAMHOST_USER@$DREAMHOST_SERVER "cd $DREAMHOST_PATH && tar -xzf redwand-ai-web.tar.gz && rm redwand-ai-web.tar.gz"

if [ $? -eq 0 ]; then
    echo "✓ Extraction successful"
else
    echo "✗ Extraction failed"
    exit 1
fi
echo ""

# Step 4: Set permissions
echo "Step 4: Setting file permissions..."
ssh $DREAMHOST_USER@$DREAMHOST_SERVER "cd $DREAMHOST_PATH && find . -type d -exec chmod 755 {} \; && find . -type f -exec chmod 644 {} \;"

if [ $? -eq 0 ]; then
    echo "✓ Permissions set"
else
    echo "✗ Permission setting failed"
    exit 1
fi
echo ""

# Step 5: Verify deployment
echo "Step 5: Verifying deployment..."
echo ""
echo "Deployment URL: https://desmond-digital.com/flip"
echo ""
echo "Files deployed:"
ssh $DREAMHOST_USER@$DREAMHOST_SERVER "cd $DREAMHOST_PATH && ls -lh"

echo ""
echo "==================================="
echo "Deployment Complete!"
echo "==================================="
echo ""
echo "Next steps:"
echo "1. Visit: https://desmond-digital.com/flip"
echo "2. Test all pages and functionality"
echo "3. Configure production Stripe keys if needed"
echo ""
