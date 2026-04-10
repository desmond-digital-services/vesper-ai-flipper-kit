#!/bin/bash
# Deploy RedWand using dreamhost-manager skill

# Load credentials
source ~/clawdbot/skills/dreamhost-manager/.env

DREAMHOST_SERVER=$DREAMHOST_SERVER
DREAMHOST_USER=$DREAMHOST_USER
DREAMHOST_PATH=$DREAMHOST_PATH

echo "==================================="
echo "RedWand - Deploy via DreamHost Manager Skill"
echo "==================================="
echo ""
echo "Server: $DREAMHOST_SERVER"
echo "User: $DREAMHOST_USER"
echo "Path: $DREAMHOST_PATH"
echo ""

# Step 1: Create deployment package
echo "Step 1: Creating deployment package..."
cd ~/clawd/projects/redwand-ai
tar -czf redwand-ai-web.tar.gz --exclude='.DS_Store' web/

if [ $? -eq 0 ]; then
    echo "✓ Package created: redwand-ai-web.tar.gz"
    ls -lh redwand-ai-web.tar.gz
else
    echo "✗ Package creation failed"
    exit 1
fi
echo ""

# Step 2: Upload to DreamHost using skill
echo "Step 2: Uploading via dreamhost-manager skill..."
echo ""
echo "NOTE: Using sftp_operations.py from dreamhost-manager skill"
echo ""

cd ~/clawdbot/skills/dreamhost-manager

# Activate virtual environment and upload
if [ -d "venv" ]; then
    source venv/bin/activate
    
    # Check if sftp_operations.py exists
    if [ -f "scripts/sftp_operations.py" ]; then
        echo "Uploading redwand-ai-web.tar.gz to $DREAMHOST_PATH..."
        python scripts/sftp_operations.py upload ~/clawd/projects/redwand-ai/redwand-ai-web.tar.gz $DREAMHOST_PATH/redwand-ai-web.tar.gz
        
        if [ $? -eq 0 ]; then
            echo "✓ Upload successful"
        else
            echo "✗ Upload failed"
            exit 1
        fi
    else
        echo "✗ sftp_operations.py not found"
        echo "Skill scripts directory is missing or incomplete"
        ls -la scripts/
        exit 1
    fi
    
    deactivate
else
    echo "✗ Virtual environment not found in dreamhost-manager skill"
    echo "Please run: cd ~/clawdbot/skills/dreamhost-manager && pip install -r requirements.txt"
    exit 1
fi
echo ""

# Step 3: Extract on server
echo "Step 3: Extracting files on server..."
python scripts/ssh_commands.py exec "cd $DREAMHOST_PATH && tar -xzf redwand-ai-web.tar.gz && rm redwand-ai-web.tar.gz"

if [ $? -eq 0 ]; then
    echo "✓ Extraction successful"
else
    echo "✗ Extraction failed"
    exit 1
fi
echo ""

# Step 4: Set permissions
echo "Step 4: Setting file permissions..."
python scripts/ssh_commands.py chmod-recursive $DREAMHOST_PATH 644 755

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
python scripts/sftp_operations.py list $DREAMHOST_PATH
echo ""

echo "==================================="
echo "Deployment Complete!"
echo "==================================="
echo ""
echo "Deployment URL: https://desmond-digital.com/flip"
echo ""
echo "Next steps:"
echo "1. Visit: https://desmond-digital.com/flip"
echo "2. Test all pages and functionality"
echo "3. Verify responsive design on mobile"
echo ""
