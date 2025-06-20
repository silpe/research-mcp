# Research MCP Server Deployment Summary

## Overview
Deployed a FastMCP server to Render that provides three research tools:
- PubMed search
- Semantic Scholar search (with rate limiting)
- Reddit search

## Project Structure
```
/Users/justinsilpe/research-mcp/
├── server.py          # Main FastMCP server with 3 tools
├── requirements.txt   # Python dependencies
└── .venv/            # Python virtual environment
```

## Deployment Details

### GitHub Repository
- URL: https://github.com/silpe/research-mcp
- Branch: main

### Render Service
- URL: https://research-mcp.onrender.com
- Service Type: Web Service (Free tier)
- Start Command: `uvicorn server:app --host 0.0.0.0 --port $PORT`

### Environment Variables (configured in Render)
```
NCBI_API_KEY=<YOUR_NCBI_API_KEY>
S2_API_KEY=<YOUR_S2_API_KEY>
REDDIT_CLIENT_ID=<YOUR_REDDIT_CLIENT_ID>
REDDIT_CLIENT_SECRET=<YOUR_REDDIT_CLIENT_SECRET>
MCP_AUTH_TOKEN=<GENERATE_A_SECURE_TOKEN>
```

### MCP Registration
```bash
# Without authentication (old, insecure):
# claude mcp add researchhub -t http https://research-mcp.onrender.com/mcp

# With authentication (secure):
claude mcp add researchhub -t http https://research-mcp.onrender.com/mcp -H "Authorization: Bearer YOUR_TOKEN"
```

## Key Implementation Details

1. **FastMCP v2 Compatibility**: The server uses `app = mcp.http_app()` to create the ASGI app for uvicorn.

2. **Rate Limiting**: Semantic Scholar API has a 1 request/second rate limit implemented in `_respect_rate_limit()`.

3. **Reddit OAuth**: Uses client credentials flow to get access tokens for Reddit API.

## Testing Commands

After restarting Claude Code:
```
# In a new Claude conversation:
"Using the researchhub MCP server, search PubMed for 'human milk oligosaccharides'"
"Search Semantic Scholar for 'mastitis inflammation' papers"
"Search Reddit for discussions about 'breastfeeding stress'"
```

## Troubleshooting

1. **MCP not loading**: Restart Claude Code (`exit` then `claude`)
2. **Check MCP servers**: `claude mcp list`
3. **Render logs**: Go to Render dashboard → research-mcp → Logs tab
4. **Test endpoint**: The MCP endpoint is at `/mcp` path

## Next Steps

- The server auto-deploys when you push to GitHub
- Render free tier sleeps after 15 min inactivity (60s wake time)
- To stay always-on: upgrade to Render Starter ($7/mo)

## File Locations
- This summary: `/Users/justinsilpe/research-mcp/DEPLOYMENT_SUMMARY.md`
- Server code: `/Users/justinsilpe/research-mcp/server.py`