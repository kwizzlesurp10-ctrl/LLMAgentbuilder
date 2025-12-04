#!/bin/bash
# Setup script for GitHub MCP Server in Cursor
# Follows instructions from GITHUB_MCP_SETUP.md

set -e

echo "🔧 Setting up GitHub MCP Server for Cursor..."
echo ""

# Check if Cursor config directory exists
CURSOR_CONFIG_DIR="$HOME/.cursor"
if [ ! -d "$CURSOR_CONFIG_DIR" ]; then
    echo "Creating Cursor config directory: $CURSOR_CONFIG_DIR"
    mkdir -p "$CURSOR_CONFIG_DIR"
fi

MCP_CONFIG_FILE="$CURSOR_CONFIG_DIR/mcp.json"

# Check if jq is available for JSON manipulation
HAS_JQ=$(command -v jq || echo "")

# Check if GitHub is already configured
if [ -f "$MCP_CONFIG_FILE" ]; then
    if [ -n "$HAS_JQ" ]; then
        # Check if github server already exists
        if jq -e '.mcpServers.github' "$MCP_CONFIG_FILE" > /dev/null 2>&1; then
            echo "⚠️  GitHub MCP server is already configured in $MCP_CONFIG_FILE"
            echo ""
            echo "Current GitHub configuration:"
            jq '.mcpServers.github' "$MCP_CONFIG_FILE"
            echo ""
            read -p "Do you want to update it? (y/N): " -n 1 -r
            echo ""
            if [[ ! $REPLY =~ ^[Yy]$ ]]; then
                echo "Keeping existing configuration. Exiting."
                exit 0
            fi
        fi
    else
        # Without jq, check with grep
        if grep -q '"github"' "$MCP_CONFIG_FILE" 2>/dev/null; then
            echo "⚠️  GitHub MCP server may already be configured in $MCP_CONFIG_FILE"
            echo "   Please check manually or install 'jq' for automatic detection"
            echo ""
        fi
    fi
fi

# Prompt for GitHub PAT
echo "📝 GitHub Personal Access Token"
echo "   Get your token at: https://github.com/settings/tokens"
echo "   Required scopes: repo, read:org (or appropriate permissions)"
echo ""
read -sp "Enter your GitHub PAT (or press Enter to use placeholder): " GITHUB_PAT
echo ""

if [ -z "$GITHUB_PAT" ]; then
    GITHUB_PAT="YOUR_GITHUB_PAT"
    echo "⚠️  Using placeholder. You'll need to replace YOUR_GITHUB_PAT manually."
else
    echo "✓ Token provided (will be masked in config)"
fi

# Create or update mcp.json
if [ -f "$MCP_CONFIG_FILE" ]; then
    echo "✓ Found existing MCP config at: $MCP_CONFIG_FILE"
    
    if [ -n "$HAS_JQ" ]; then
        # Use jq to merge GitHub config
        echo "📝 Merging GitHub configuration into existing file..."
        
        # Create backup
        cp "$MCP_CONFIG_FILE" "${MCP_CONFIG_FILE}.backup"
        echo "✓ Created backup: ${MCP_CONFIG_FILE}.backup"
        
        # Merge GitHub config
        jq --arg pat "$GITHUB_PAT" \
           '.mcpServers.github = {
             "url": "https://api.githubcopilot.com/mcp/",
             "headers": {
               "Authorization": "Bearer \($pat)"
             }
           }' "$MCP_CONFIG_FILE" > "${MCP_CONFIG_FILE}.tmp" && \
        mv "${MCP_CONFIG_FILE}.tmp" "$MCP_CONFIG_FILE"
        
        echo "✓ Successfully added GitHub MCP server configuration"
    else
        echo ""
        echo "⚠️  'jq' not found. Please manually add the following to your mcpServers object:"
        echo ""
        echo '  "github": {'
        echo '    "url": "https://api.githubcopilot.com/mcp/",'
        echo '    "headers": {'
        echo "      \"Authorization\": \"Bearer $GITHUB_PAT\""
        echo '    }'
        echo '  }'
        echo ""
        echo "Current config file contents:"
        cat "$MCP_CONFIG_FILE"
        echo ""
        echo "💡 Tip: Install 'jq' for automatic configuration: sudo apt install jq (or brew install jq)"
    fi
else
    echo "Creating new MCP config file at: $MCP_CONFIG_FILE"
    cat > "$MCP_CONFIG_FILE" << EOF
{
  "mcpServers": {
    "github": {
      "url": "https://api.githubcopilot.com/mcp/",
      "headers": {
        "Authorization": "Bearer $GITHUB_PAT"
      }
    }
  }
}
EOF
    echo "✓ Created MCP config file"
fi

echo ""
echo "📋 Next steps:"
if [ "$GITHUB_PAT" = "YOUR_GITHUB_PAT" ]; then
    echo "1. Edit $MCP_CONFIG_FILE"
    echo "2. Replace YOUR_GITHUB_PAT with your actual GitHub Personal Access Token"
    echo "3. Save the file"
else
    echo "1. Configuration file is ready at: $MCP_CONFIG_FILE"
fi
echo "2. Restart Cursor completely"
echo "3. Verify in Settings → Tools & Integrations → MCP Tools (should show green dot)"
echo "4. Test by asking: 'List my GitHub repositories'"
echo ""
echo "✨ Setup script complete!"

