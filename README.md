# Research MCP Services

This repository contains two independent MCP (Model Context Protocol) services for academic research:

1. **ResearchHub MCP** - Access to Semantic Scholar, Reddit, arXiv, and CrossRef
2. **PubMed MCP** - Specialized PubMed search and retrieval

**Status**: ✅ Split into two independent services (January 2025)

## Repository Structure

```
research-mcp/
├── researchhub-mcp/
│   ├── server.py          # ResearchHub service
│   └── requirements.txt   # Dependencies
├── pubmed-mcp/
│   ├── server.py          # PubMed service
│   └── requirements.txt   # Dependencies
└── README.md             # This file
```

## Services Overview

### ResearchHub MCP

Provides access to multiple academic databases and discussion platforms:

#### Features
- **Semantic Scholar**
  - `semantic_scholar_search` - Advanced search with filtering
  - `semantic_scholar_paper_details` - Get paper details with citations
  - `semantic_scholar_citations` - Find citing papers
  - `semantic_scholar_references` - Get referenced papers
  - `semantic_scholar_author_search` - Search for authors
  - `semantic_scholar_author_papers` - Get author's publications

- **Reddit Integration**
  - `reddit_search` - Search across Reddit
  - `reddit_subreddit_search` - Search specific subreddits
  - `reddit_comments` - Fetch comment threads

- **arXiv**
  - `arxiv_search` - Search with complex queries
  - `arxiv_paper` - Get paper by ID

- **CrossRef**
  - `crossref_works_search` - Search scholarly works
  - `crossref_doi_lookup` - Lookup by DOI
  - `crossref_journal_works` - Get journal publications

- **Multi-Source**
  - `multi_database_search` - Search across all databases
  - `get_paper_by_identifier` - Get paper by DOI, arXiv ID, or S2 ID

### PubMed MCP

Specialized service for PubMed searches:

#### Features
- `pubmed_search` - Search and get full article details
- `pubmed_fetch` - Fetch details for specific PMIDs
- `pubmed_summary` - Get concise article summaries

## Deployment on Render

Both services are deployed independently on Render.com:

### ResearchHub Service
- **URL**: https://researchhub-mcp.onrender.com
- **Root Directory**: `researchhub-mcp`
- **Environment Variables**:
  - `MCP_AUTH_TOKEN` - Your authentication token
  - `S2_API_KEY` - Semantic Scholar API key (optional)
  - `REDDIT_CLIENT_ID` - Reddit OAuth client ID (optional)
  - `REDDIT_CLIENT_SECRET` - Reddit OAuth client secret (optional)

### PubMed Service
- **URL**: https://pubmed-mcp.onrender.com
- **Root Directory**: `pubmed-mcp`
- **Environment Variables**:
  - `MCP_AUTH_TOKEN` - Your authentication token (same as ResearchHub)
  - `NCBI_API_KEY` - PubMed API key (recommended)

## MCP Registration with Claude Code

### Using Claude Code CLI

Remove old service:
```bash
mcp remove researchhub
```

Add new services:
```bash
mcp add researchhub -t http https://researchhub-mcp.onrender.com -H "Authorization: Bearer YOUR_MCP_AUTH_TOKEN"
mcp add pubmed -t http https://pubmed-mcp.onrender.com -H "Authorization: Bearer YOUR_MCP_AUTH_TOKEN"
```

### Manual Configuration

Edit your Claude Desktop config file:
- **Mac**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "researchhub": {
      "url": "https://researchhub-mcp.onrender.com",
      "headers": {
        "Authorization": "Bearer YOUR_MCP_AUTH_TOKEN"
      }
    },
    "pubmed": {
      "url": "https://pubmed-mcp.onrender.com",
      "headers": {
        "Authorization": "Bearer YOUR_MCP_AUTH_TOKEN"
      }
    }
  }
}
```

## Local Development

### Running ResearchHub locally:
```bash
cd researchhub-mcp
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python server.py
```

### Running PubMed locally:
```bash
cd pubmed-mcp
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python server.py
```

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

### Test Both Services
```
Using my researchhub and pubmed MCPs, search for recent papers about "CRISPR gene editing cancer therapy" across all available databases.
```

### ResearchHub Examples
```python
# Multi-database search
results = multi_database_search("machine learning healthcare")

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

### PubMed Examples
```python
# Search with full details
articles = pubmed_search("CAR-T immunotherapy", max_results=10)

# Get specific papers
papers = pubmed_fetch(["32501203", "32501204"])

# Quick summaries
summaries = pubmed_summary(["32501203", "32501204"])
```

## Rate Limits

- **PubMed**: 10/sec with API key, 3/sec without
- **Semantic Scholar**: 1/sec (enforced in code)
- **Reddit**: Standard API limits
- **arXiv**: No hard limit, be respectful
- **CrossRef**: Generous limits

## Security

1. **Always use authentication** - Set `MCP_AUTH_TOKEN` in production
2. **Never commit API keys** - Use environment variables
3. **Generate secure tokens**: 
   ```bash
   python3 -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

## Troubleshooting

1. **Service not responding**
   - Render free tier sleeps after 15 min - wait 60s for wake up
   - Check Render dashboard logs

2. **Authentication errors**
   - Verify `MCP_AUTH_TOKEN` matches in Render and Claude
   - Include "Bearer " prefix in Authorization header

3. **Tools not appearing in Claude**
   - Restart Claude Code completely
   - Run `mcp list` to verify registration
   - Check service URLs are accessible

4. **Rate limit errors**
   - Add API keys for higher limits
   - Implement delays between requests

## Repository Information

- **GitHub**: https://github.com/silpe/research-mcp
- **Author**: Justin Silpe
- **License**: MIT
- **Last Updated**: January 2025