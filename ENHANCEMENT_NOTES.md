# Research MCP Enhancement Notes
*Date: 2025-06-20*

## Overview
Enhanced the ResearchHub MCP server to include full BioMCP functionality and additional research tools.

## Changes Made

### 1. Created Enhanced Server (`server_enhanced.py`)
Added comprehensive research functionality:

#### Enhanced PubMed Tools
- `pubmed_fetch`: Retrieves complete article details (title, abstract, authors, journal, DOI, keywords)
- `pubmed_summary`: Provides concise article summaries with key metadata

#### Enhanced Semantic Scholar Features  
- `semantic_scholar_paper_details`: Get comprehensive paper information
- `semantic_scholar_citations`: Find papers that cite a given paper
- `semantic_scholar_references`: Get papers referenced by a given paper
- `semantic_scholar_author_search`: Search for authors by name
- `semantic_scholar_author_papers`: Get all papers by a specific author

#### Enhanced Reddit Integration
- Modified `reddit_search`: Added content type filtering (links, self-posts, all)
- `reddit_subreddit_search`: Search within specific subreddits
- `reddit_comments`: Fetch full comment threads for submissions

#### New Research Sources
- **arXiv Integration**:
  - `arxiv_search`: Full search with sort options and PDF links
  - `arxiv_paper`: Get specific paper by ID
  
- **CrossRef Integration**:
  - `crossref_works_search`: Search scholarly works with filters
  - `crossref_doi_lookup`: Look up works by DOI
  - `crossref_journal_works`: Get recent journal publications

### 2. Deployment Steps Taken
1. Backed up original server: `cp server.py server_original.py`
2. Replaced server with enhanced version: `cp server_enhanced.py server.py`
3. Fixed MCP name to maintain consistency ("ResearchHub" not "ResearchHub Enhanced")
4. Committed and pushed to GitHub for automatic Render deployment

### 3. MCP Registration Update
```bash
# Remove old registration
claude mcp remove researchhub

# Re-add (without auth)
claude mcp add researchhub -t http https://research-mcp.onrender.com/mcp

# Or with auth if MCP_AUTH_TOKEN is set in Render
claude mcp add researchhub -t http https://research-mcp.onrender.com/mcp -H "Authorization: Bearer YOUR_TOKEN"
```

## Important Notes

### Backward Compatibility
- All original endpoints remain unchanged
- Existing functionality preserved
- New features are additions only

### Environment Variables
No new environment variables required. Uses same ones as original:
- `NCBI_API_KEY` (PubMed)
- `S2_API_KEY` (Semantic Scholar)
- `REDDIT_CLIENT_ID` & `REDDIT_CLIENT_SECRET`
- `MCP_AUTH_TOKEN` (optional authentication)

### Dependencies
No new dependencies needed - all functionality uses Python standard library and existing `requests` package.

### Render Deployment
- Automatic deployment triggered by GitHub push
- No manual intervention needed with free tier
- Monitor deployment at: https://dashboard.render.com
- Service spins down after 15 min inactivity (normal for free tier)

## Usage Examples

### Enhanced PubMed
```python
# Get full article details
pmids = pubmed_search("CRISPR therapy", max_results=5)
articles = pubmed_fetch(pmids)  # Returns dict with full metadata
summaries = pubmed_summary(pmids)  # Returns concise summaries
```

### Paper Network Analysis
```python
# Find citation network
paper = semantic_scholar_search("transformer architecture")[0]
citations = semantic_scholar_citations(paper["paperId"])
references = semantic_scholar_references(paper["paperId"])
```

### Reddit Research
```python
# Search specific subreddit with comments
posts = reddit_subreddit_search("science", "quantum computing")
comments = reddit_comments(posts[0]["id"])
```

### Cross-Database Search
```python
# Search multiple sources
arxiv_results = arxiv_search("quantum machine learning")
crossref_results = crossref_works_search("quantum machine learning")
pubmed_ids = pubmed_search("quantum machine learning")
```

## Files Modified/Created
- `server.py` - Replaced with enhanced version
- `server_enhanced.py` - Full enhanced server (backup)
- `server_original.py` - Original server (backup)
- `README_ENHANCED.md` - Comprehensive documentation
- `ENHANCEMENT_NOTES.md` - This file

## Next Steps
1. Wait for Render deployment to complete (~2-5 minutes)
2. Test new functionality through Claude
3. Consider adding more research sources:
   - Google Scholar (if API becomes available)
   - ORCID integration
   - PubMed Central full text
   - bioRxiv/medRxiv