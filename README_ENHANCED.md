# Enhanced ResearchHub MCP Server

This enhanced version of the ResearchHub MCP server provides comprehensive research tools with full BioMCP functionality, enhanced Semantic Scholar features, improved Reddit integration, and additional research sources.

## New Features

### Enhanced PubMed Integration
- **pubmed_search**: Original search functionality (returns PubMed IDs)
- **pubmed_fetch**: Fetch complete article details including:
  - Title, abstract, authors
  - Journal information and publication year
  - DOI and keywords
  - Supports batch fetching (up to 10 articles at once)
- **pubmed_summary**: Get concise summaries of articles with key metadata

### Enhanced Semantic Scholar Features
- **semantic_scholar_search**: Enhanced search with more fields (authors, abstract, citation count)
- **semantic_scholar_paper_details**: Get comprehensive paper information
- **semantic_scholar_citations**: Find papers that cite a given paper
- **semantic_scholar_references**: Get papers referenced by a given paper
- **semantic_scholar_author_search**: Search for authors by name
- **semantic_scholar_author_papers**: Get all papers by a specific author

### Enhanced Reddit Integration
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

### PubMed Examples
```python
# Search and fetch full details
pmids = pubmed_search("CRISPR gene editing", max_results=5)
articles = pubmed_fetch(pmids)

# Get summaries
summaries = pubmed_summary(pmids)
```

### Semantic Scholar Examples
```python
# Search with enhanced fields
papers = semantic_scholar_search("machine learning healthcare", limit=10)

# Get paper details and citations
paper_id = papers[0]["paperId"]
details = semantic_scholar_paper_details(paper_id)
citations = semantic_scholar_citations(paper_id, limit=20)

# Search for author and their papers
authors = semantic_scholar_author_search("Geoffrey Hinton", limit=5)
author_papers = semantic_scholar_author_papers(authors[0]["authorId"])
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

Required environment variables:
- `NCBI_API_KEY`: For PubMed API (optional but recommended)
- `S2_API_KEY`: For Semantic Scholar API (optional but recommended)
- `REDDIT_CLIENT_ID`: For Reddit OAuth
- `REDDIT_CLIENT_SECRET`: For Reddit OAuth
- `MCP_AUTH_TOKEN`: For authentication (optional)

## Running the Enhanced Server

```bash
python server_enhanced.py
```

Or with uvicorn:
```bash
uvicorn server_enhanced:app --host 0.0.0.0 --port 8000
```

## Rate Limits

- **PubMed**: 10 requests/second with API key, 3/second without
- **Semantic Scholar**: 1 request/second (enforced in code)
- **Reddit**: Follows Reddit API rate limits
- **arXiv**: Be respectful, no hard limit but avoid excessive requests
- **CrossRef**: Generous limits, but use User-Agent header