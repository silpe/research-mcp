# Research MCP Service

A unified MCP (Model Context Protocol) service providing access to multiple academic research databases and platforms.

**Status**: ✅ Running remotely on Render for Claude Code (January 2025)
**IMPORTANT**: This service runs REMOTELY on Render, NOT locally. Configuration is for Claude Code only (not Claude Desktop).

## Features

### Academic Databases
- **PubMed** - Biomedical literature search and retrieval
- **Semantic Scholar** - AI-powered research paper database
- **arXiv** - Preprint repository for scientific papers
- **CrossRef** - Scholarly metadata and DOI lookup

### Additional Sources
- **Reddit Integration** - Academic discussions and community insights

### Multi-Source Capabilities
- Search across all databases simultaneously
- Retrieve papers by DOI, arXiv ID, or Semantic Scholar ID

## Remote Deployment on Render

This service is deployed remotely on Render at: `https://research-mcp.onrender.com`

### Claude Code Configuration

To use this service with Claude Code, add the following to your `~/.config/claude-code/config.json`:

```json
{
  "mcpServers": {
    "researchhub": {
      "transport": {
        "type": "http",
        "url": "https://research-mcp.onrender.com/mcp",
        "headers": {
          "Authorization": "Bearer YOUR_MCP_AUTH_TOKEN"
        }
      }
    }
  }
}
```

After adding this configuration, restart Claude Code to connect to the remote MCP server.

### Environment Variables (Set in Render Dashboard)

The following environment variables must be configured in your Render deployment:

- `MCP_AUTH_TOKEN` - Your secure authentication token
- `NCBI_API_KEY` - Your PubMed API key
- `S2_API_KEY` - Your Semantic Scholar API key
- `REDDIT_CLIENT_ID` - Your Reddit client ID
- `REDDIT_CLIENT_SECRET` - Your Reddit client secret

## Available Functions

### PubMed
- `pubmed_search` - Search and get full article details
- `pubmed_fetch` - Fetch details for specific PMIDs
- `pubmed_summary` - Get concise article summaries

### Semantic Scholar
- `semantic_scholar_search` - Advanced search with filtering
- `semantic_scholar_paper_details` - Get paper details with citations
- `semantic_scholar_citations` - Find citing papers
- `semantic_scholar_references` - Get referenced papers
- `semantic_scholar_author_search` - Search for authors
- `semantic_scholar_author_papers` - Get author's publications

### Reddit
- `reddit_search` - Search across Reddit
- `reddit_subreddit_search` - Search specific subreddits
- `reddit_comments` - Fetch comment threads

### arXiv
- `arxiv_search` - Search with complex queries
- `arxiv_paper` - Get paper by ID

### CrossRef
- `crossref_works_search` - Search scholarly works
- `crossref_doi_lookup` - Lookup by DOI
- `crossref_journal_works` - Get journal publications

### Multi-Source
- `multi_database_search` - Search across all databases
- `get_paper_by_identifier` - Get paper by DOI, arXiv ID, or S2 ID

## API Keys

### Getting API Keys
1. **PubMed (NCBI)**: https://ncbiinsights.ncbi.nlm.nih.gov/api-keys/
2. **Semantic Scholar**: https://www.semanticscholar.org/product/api
3. **Reddit**: https://www.reddit.com/prefs/apps (create a "script" app)

### Why API Keys Matter
- **PubMed**: 10 requests/second with key vs 3/second without
- **Semantic Scholar**: Higher rate limits with key
- **Reddit**: Required for authenticated access

## Usage Examples

### Search across all databases
```
Search for recent papers about "CRISPR gene editing cancer therapy" across all available databases.
```

### Specific database searches
```python
# PubMed search
articles = pubmed_search("CAR-T immunotherapy", max_results=10)

# Semantic Scholar with filters
papers = semantic_scholar_search(
    "deep learning",
    year_range="2023-2024",
    min_citations=50
)

# Reddit discussions
posts = reddit_subreddit_search("MachineLearning", "transformer models")

# Get paper by DOI
paper = get_paper_by_identifier("10.1038/nature12373")
```

## Rate Limits

- **PubMed**: 10/sec with API key, 3/sec without
- **Semantic Scholar**: 1/sec (enforced in code)
- **Reddit**: Standard API limits
- **arXiv**: No hard limit, be respectful
- **CrossRef**: Generous limits

## Troubleshooting

1. **MCP not loading in Claude Code**
   - Ensure `~/.config/claude-code/config.json` contains the correct configuration
   - Verify the Render service is running at `https://research-mcp.onrender.com`
   - Restart Claude Code after configuration changes
   - Note: Free Render tier may take up to 60 seconds to wake up on first request

2. **Authentication errors**
   - Verify your MCP_AUTH_TOKEN in the config matches the one set in Render
   - Check that all API keys are correctly set in Render's environment variables

3. **Rate limit errors**
   - Ensure API keys are configured in Render dashboard
   - The service implements automatic rate limiting for each API

4. **Connection timeouts**
   - Free Render services sleep after inactivity
   - First request may take longer as the service wakes up
   - Subsequent requests will be faster

## Security

1. **Never commit API keys or tokens** to the repository
2. **All sensitive data should be stored in Render environment variables**
3. **Generate secure tokens**: 
   ```bash
   python3 -c "import secrets; print(secrets.token_urlsafe(32))"
   ```
4. **The MCP_AUTH_TOKEN in your Claude Code config** should match the one in Render

## Repository Information

- **Author**: Justin Silpe
- **License**: MIT
- **Last Updated**: January 2025