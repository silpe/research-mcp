# Secure MCP Configuration

## Steps to Secure Your MCP Server:

### 1. Generate a Secure Token
```bash
# Generate a secure random token
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 2. Update Render Environment Variables
1. Go to your Render dashboard
2. Navigate to research-mcp service
3. Go to Environment tab
4. Add: `MCP_AUTH_TOKEN=<your-generated-token>`
5. Update server.py to server_secure.py in your GitHub repo

### 3. Update MCP Registration with Authentication
```bash
# Remove the old registration
claude mcp remove researchhub

# Add with authentication
claude mcp add researchhub \
  --transport http \
  --url https://research-mcp.onrender.com/mcp \
  --header "Authorization: Bearer <your-token>"
```

### 4. Alternative: Use SSH Tunnel (Most Secure)
Instead of exposing your server publicly, run it locally and use SSH:

```bash
# On your local machine
claude mcp add researchhub --transport stdio python /path/to/server.py
```

### 5. Security Best Practices:
- **NEVER** commit API keys to GitHub
- Rotate your authentication token regularly
- Consider IP whitelisting on Render (requires paid plan)
- Monitor usage logs on Render dashboard
- Use environment variables for all sensitive data

### 6. Testing Authentication:
```bash
# Test without auth (should fail)
curl https://research-mcp.onrender.com/mcp

# Test with auth (should work)
curl -H "Authorization: Bearer <your-token>" https://research-mcp.onrender.com/mcp
```