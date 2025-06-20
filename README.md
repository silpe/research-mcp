# ResearchHub MCP Server

A comprehensive research tools MCP server that provides access to PubMed, Semantic Scholar, Reddit, arXiv, and CrossRef APIs. Features include full paper metadata, citation networks, author search, and more.

## Features

### ✨ NEW: Enhanced Search Capabilities
- **multi_database_search**: Search multiple databases simultaneously
- **get_paper_by_identifier**: Retrieve papers using DOI, PMID, arXiv ID, or S2 ID

### PubMed Integration (Enhanced)
- **pubmed_search**: Now returns full article details by default!
  - Complete article metadata (title, authors, abstract, journal, year)
  - Formatted author lists (e.g., "Smith J, Jones A et al.")
  - DOI and keywords included
  - Optional `return_details=False` for legacy PMID-only mode
- **pubmed_fetch**: Fetch complete article details for specific PMIDs
- **pubmed_summary**: Get concise summaries of articles with key metadata

### Semantic Scholar Features (Enhanced)
- **semantic_scholar_search**: Advanced search with filtering
  - Year range filtering (e.g., `year_range="2020-2024"`)
  - Minimum citation filtering (e.g., `min_citations=50`)
  - Fields of study filtering
  - Returns citation metrics, PDF links, venue info
  - Formatted author lists included
- **semantic_scholar_paper_details**: Enhanced with citation metrics and PDF links
- **semantic_scholar_citations**: Find papers that cite a given paper
- **semantic_scholar_references**: Get papers referenced by a given paper
- **semantic_scholar_author_search**: Search for authors by name
- **semantic_scholar_author_papers**: Get all papers by a specific author

### Reddit Integration
- **reddit_search**: Enhanced with content type filtering (links, self-posts, all)
- **reddit_subreddit_search**: Search within specific subreddits
- **reddit_comments**: Fetch comment threads for any submission

### arXiv Integration
- **arxiv_search**: Search arXiv with support for:
  - Complex query syntax
  - Sort options (relevance, date)
  - Full paper metadata including PDF links
- **arxiv_paper**: Get details for a specific arXiv paper by ID

### CrossRef Integration
- **crossref_works_search**: Search scholarly works with filtering options
- **crossref_doi_lookup**: Look up specific works by DOI
- **crossref_journal_works**: Get recent publications from specific journals

## Usage Examples

### NEW: Multi-Database Search
```python
# Search all databases at once
results = multi_database_search("CRISPR gene therapy")
# Returns: {"pubmed": [...], "semantic_scholar": [...], "arxiv": [...], "crossref": [...]}

# Search specific databases
results = multi_database_search(
    "CAR-T immunotherapy", 
    databases=["pubmed", "semantic_scholar"],
    max_results_per_db=5
)

# Get paper by any identifier
paper = get_paper_by_identifier("10.1038/nature12373")  # DOI
paper = get_paper_by_identifier("32501203")              # PMID
paper = get_paper_by_identifier("2301.08727")            # arXiv ID
```

### PubMed Examples (Enhanced)
```python
# NEW: Get full details directly (default behavior)
articles = pubmed_search("CRISPR gene editing", max_results=5)
# Returns complete article info with authors, abstracts, etc.

# Legacy mode: get only PMIDs
pmids = pubmed_search("CRISPR", max_results=5, return_details=False)

# Get summaries
summaries = pubmed_summary(["32501203", "32501204"])
```

### Semantic Scholar Examples (Enhanced)
```python
# NEW: Search with filters
papers = semantic_scholar_search(
    "machine learning healthcare",
    limit=10,
    year_range="2022-2024",
    min_citations=50,
    fields_of_study=["Computer Science", "Medicine"]
)

# Access enhanced data
for paper in papers:
    print(f"Title: {paper['title']}")
    print(f"Authors: {paper['author_list']}")  # Formatted list
    print(f"Citations: {paper['citation_metrics']['total']}")
    print(f"PDF available: {paper['has_pdf']}")
    print(f"Venue: {paper['venue_info']}")

# Get enhanced paper details
details = semantic_scholar_paper_details(paper_id)
print(f"Influential citations: {details['citation_metrics']['influential']}")
print(f"PDF URL: {details['pdf_url']}")
```

### Reddit Examples
```python
# Search all of Reddit
results = reddit_search("machine learning", sort="top", search_type="all")

# Search specific subreddit
ml_posts = reddit_subreddit_search("MachineLearning", "transformer", limit=10)

# Get comments
submission_id = results[0]["id"]
comments = reddit_comments(submission_id, limit=50)
```

### arXiv Examples
```python
# Search with arXiv syntax
papers = arxiv_search("cat:cs.AI AND ti:transformer", max_results=10)

# Get specific paper
paper = arxiv_paper("2301.00000")
```

### CrossRef Examples
```python
# Search with filters
results = crossref_works_search(
    "climate change", 
    rows=20,
    filter_dict={"from-pub-date": "2023-01-01"}
)

# DOI lookup
work = crossref_doi_lookup("10.1038/nature12373")

# Journal works
journal_papers = crossref_journal_works("0028-0836", rows=10)  # Nature ISSN
```

## Environment Variables

Configure these in your environment or Render dashboard:

### API Keys
- `NCBI_API_KEY`: PubMed API key (optional but recommended for higher rate limits)
- `S2_API_KEY`: Semantic Scholar API key (optional but recommended)
- `REDDIT_CLIENT_ID`: Reddit OAuth client ID (required for Reddit features)
- `REDDIT_CLIENT_SECRET`: Reddit OAuth client secret (required for Reddit features)

### Security
- `MCP_AUTH_TOKEN`: Authentication token for MCP server access (recommended for production)

### Getting API Keys
1. **PubMed**: Register at https://www.ncbi.nlm.nih.gov/account/
2. **Semantic Scholar**: Register at https://www.semanticscholar.org/product/api
3. **Reddit**: Create app at https://www.reddit.com/prefs/apps

## Deployment

### Deployed Service
- **URL**: https://research-mcp.onrender.com
- **MCP Endpoint**: https://research-mcp.onrender.com/mcp
- **Service**: Render.com (Free tier - sleeps after 15 min inactivity)
- **GitHub**: https://github.com/silpe/research-mcp

### MCP Registration

#### With Authentication (Secure - Recommended)
```bash
# Remove old registration if exists
claude mcp remove researchhub

# Add with authentication
claude mcp add researchhub -t http https://research-mcp.onrender.com/mcp -H "Authorization: Bearer YOUR_MCP_AUTH_TOKEN"
```

#### Without Authentication (Testing only)
```bash
claude mcp add researchhub -t http https://research-mcp.onrender.com/mcp
```

### Running Locally

```bash
# Install dependencies
pip install -r requirements.txt

# Run server
python server.py
```

Or with uvicorn:
```bash
uvicorn server:app --host 0.0.0.0 --port 8000
```

## Rate Limits

- **PubMed**: 10 requests/second with API key, 3/second without
- **Semantic Scholar**: 1 request/second (enforced in code)
- **Reddit**: Follows Reddit API rate limits
- **arXiv**: Be respectful, no hard limit but avoid excessive requests
- **CrossRef**: Generous limits, but use User-Agent header

## Security Considerations

1. **Always use authentication in production** - Set `MCP_AUTH_TOKEN` in Render
2. **Never commit API keys** - Use environment variables
3. **Rotate tokens regularly** - Generate new tokens with: `python3 -c "import secrets; print(secrets.token_urlsafe(32))"`
4. **Monitor usage** - Check Render logs for unauthorized access attempts

## Troubleshooting

1. **Service not responding**: 
   - Render free tier sleeps after 15 min - wait 60s for wake up
   - Check Render dashboard for deployment status

2. **Authentication errors**:
   - Verify MCP_AUTH_TOKEN is set in Render environment
   - Ensure Authorization header is included in MCP registration

3. **Rate limit errors**:
   - Add API keys for higher limits
   - Semantic Scholar enforces 1 req/sec regardless of API key

4. **MCP not working**:
   - Restart Claude Code: `exit` then `claude`
   - Check registered servers: `claude mcp list`
   - Re-register the server with correct authentication