# Deploy to Render - Step by Step

## Quick Deploy (One Click)

1. Click this button to deploy directly to Render:
   [![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/silpe/research-mcp)

2. Fill in the required environment variables when prompted:
   - **MCP_AUTH_TOKEN**: `1S8q-XGU6zVZ56n9WotKv5IKKlMDPYw7e3ONBEN0wGU`
   - **S2_API_KEY**: (Get from https://www.semanticscholar.org/product/api)
   - **REDDIT_CLIENT_ID**: (Optional - from https://www.reddit.com/prefs/apps)
   - **REDDIT_CLIENT_SECRET**: (Optional - from Reddit app settings)

## Manual Deploy

If the button doesn't work, follow these steps:

1. **Go to Render Dashboard**: https://dashboard.render.com

2. **Create New Web Service**:
   - Click "New +" → "Web Service"
   - Connect your GitHub account if not already connected
   - Select repository: `silpe/research-mcp`
   - Fill in details:
     - **Name**: research-mcp
     - **Region**: Choose closest to you
     - **Branch**: main
     - **Runtime**: Python 3
     - **Build Command**: `pip install -r requirements.txt`
     - **Start Command**: `python -m uvicorn server:app --host 0.0.0.0 --port $PORT`

3. **Add Environment Variables**:
   Click "Advanced" and add:
   - `MCP_AUTH_TOKEN` = `1S8q-XGU6zVZ56n9WotKv5IKKlMDPYw7e3ONBEN0wGU`
   - `S2_API_KEY` = (your Semantic Scholar API key)
   - `REDDIT_CLIENT_ID` = (optional)
   - `REDDIT_CLIENT_SECRET` = (optional)

4. **Create Web Service**

## After Deployment

1. Wait for the build to complete (usually 2-5 minutes)

2. Your service URL will be: `https://research-mcp.onrender.com`

3. Update your Claude Code config at `~/.config/claude-code/config.json`:
```json
{
  "mcpServers": {
    "researchhub": {
      "transport": {
        "type": "http",
        "url": "https://research-mcp.onrender.com/mcp",
        "headers": {
          "Authorization": "Bearer 1S8q-XGU6zVZ56n9WotKv5IKKlMDPYw7e3ONBEN0wGU"
        }
      }
    }
  }
}
```

4. Restart Claude Code to connect to your deployed MCP server

## Troubleshooting

- If deployment fails, check the Render logs
- Free tier services sleep after 15 minutes of inactivity
- First request after sleep takes ~30 seconds to wake up
- Make sure all environment variables are set correctly