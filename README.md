# Research MCP Service

A unified MCP (Model Context Protocol) service providing access to multiple academic research databases and platforms, deployed remotely on Render.

**Status**: ✅ Remote deployment on Render  
**Compatible with**: Claude Code (using `mcp` command)  
**Service URL**: https://research-mcp.onrender.com

## Available Research Tools

### 📚 PubMed
- `pubmed_search` - Search biomedical literature
- `pubmed_fetch` - Get full article details
- `pubmed_summary` - Get concise article summaries

### 🎓 Semantic Scholar
- `semantic_scholar_search` - AI-powered paper search
- `semantic_scholar_paper_details` - Detailed paper information
- `semantic_scholar_citations` - Get citing papers
- `semantic_scholar_references` - Get paper references
- `semantic_scholar_author_search` - Find authors
- `semantic_scholar_author_papers` - Get author's publications

### 💬 Reddit
- `reddit_search` - Search Reddit posts
- `reddit_subreddit_search` - Search within subreddits
- `reddit_comments` - Get post comments

### 📄 arXiv
- `arxiv_search` - Search preprint repository
- `arxiv_paper` - Get specific paper details

### 🔍 CrossRef
- `crossref_works_search` - Search scholarly works
- `crossref_doi_lookup` - Look up by DOI
- `crossref_journal_works` - Get journal publications

## Setup Instructions

### 1. Deploy to Render

1. Go to [Render Dashboard](https://dashboard.render.com)
2. Create new Web Service
3. Connect repository: `silpe/research-mcp`
4. Configure:
   - **Name**: `research-mcp`
   - **Branch**: `main`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python -m uvicorn server:app --host 0.0.0.0 --port $PORT`

5. Add environment variables:
   ```
   MCP_AUTH_TOKEN = [your-generated-token]
   S2_API_KEY = [Semantic Scholar API key]
   REDDIT_CLIENT_ID = [Reddit app ID]
   REDDIT_CLIENT_SECRET = [Reddit app secret]
   NCBI_API_KEY = [NCBI API key]
   ```

### 2. Connect with Claude Code

After deployment completes, run this single command:

```bash
mcp add researchhub -t http https://research-mcp.onrender.com/mcp -H "Authorization: Bearer YOUR_MCP_AUTH_TOKEN"
```

Replace `YOUR_MCP_AUTH_TOKEN` with the token you set in Render.

### 3. Verify Connection

In Claude Code, you should see the ResearchHub tools available. Test with:
- "Search PubMed for CRISPR"
- "Find papers about machine learning on Semantic Scholar"
- "Search arXiv for quantum computing"

## Troubleshooting

### Service not responding
- Free Render services sleep after 15 minutes of inactivity
- First request may take ~30 seconds to wake up
- Check Render dashboard for deployment status

### Authentication errors
- Ensure the MCP_AUTH_TOKEN in your command matches the one in Render
- Token should be in format: `Bearer YOUR_TOKEN`

### Rate limiting
- Semantic Scholar: 1 request/second
- Reddit: Automatic token refresh
- PubMed: Uses NCBI API key for higher limits

## Security Notes

- Never commit API keys to the repository
- All API keys should be set in Render environment variables
- Generate secure tokens: `python3 -c "import secrets; print(secrets.token_urlsafe(32))"`

## Development

To contribute or run locally for testing:
1. Clone the repository
2. Create `.env` file with API keys
3. Run: `python server.py`

## License

MIT License - See LICENSE file for details

---
**Author**: Justin Silpe  
**Last Updated**: January 2025