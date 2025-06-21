# ResearchHub MCP Improvements

## Summary of Enhancements

### 1. Enhanced PubMed Search
The `pubmed_search` function now returns full article details by default instead of just PMIDs:

**Before:**
- Returned only a list of PubMed IDs
- Required a separate call to get article details

**After:**
- Returns complete article information including:
  - Title, authors, journal, year
  - Full abstract
  - DOI and keywords
  - Formatted author list (e.g., "Smith J, Jones A, Brown C et al.")
- Added `return_details` parameter for backward compatibility

### 2. Enhanced Semantic Scholar Search
The `semantic_scholar_search` function now includes:

**New Features:**
- **Additional metadata**: Citation counts (total and influential), venue information, open access PDFs
- **Advanced filtering**:
  - `year_range`: Filter by publication year (e.g., "2020-2024")
  - `min_citations`: Filter by minimum citation count
  - `fields_of_study`: Filter by research fields
- **Enhanced output**:
  - Formatted author lists
  - Citation metrics object
  - Direct PDF URLs when available
  - Publication venue information

### 3. Enhanced Paper Details
The `semantic_scholar_paper_details` function now provides:
- Influential citation counts
- Year-by-year citation data
- Open access PDF links
- DOI and arXiv identifiers
- Formatted author information

### 4. New Combined Search Functions

#### `multi_database_search`
Search multiple databases simultaneously:
```python
# Search all databases at once
results = multi_database_search("CRISPR gene therapy")

# Search specific databases
results = multi_database_search(
    "CAR-T immunotherapy", 
    databases=["pubmed", "semantic_scholar"],
    max_results_per_db=5
)
```

#### `get_paper_by_identifier`
Retrieve paper details using any identifier:
```python
# Auto-detects identifier type
paper = get_paper_by_identifier("10.1038/nature12373")  # DOI
paper = get_paper_by_identifier("32501203")              # PMID
paper = get_paper_by_identifier("2301.08727")            # arXiv
```

## Usage Examples

### Example 1: Enhanced PubMed Search
```python
# Get full article details
articles = pubmed_search("CAR-T cell therapy", max_results=5)
# Returns: [{"pmid": "...", "title": "...", "authors": [...], "abstract": "...", ...}]

# Get only PMIDs (legacy mode)
pmids = pubmed_search("CAR-T cell therapy", max_results=5, return_details=False)
# Returns: ["12345678", "23456789", ...]
```

### Example 2: Semantic Scholar with Filters
```python
# Search recent highly-cited papers
papers = semantic_scholar_search(
    "transformer neural networks",
    year_range="2020-2024",
    min_citations=100,
    fields_of_study=["Computer Science"]
)
```

### Example 3: Multi-Database Search
```python
# Compare results across databases
all_results = multi_database_search("CRISPR base editing")
print(f"PubMed: {len(all_results['pubmed'])} results")
print(f"Semantic Scholar: {len(all_results['semantic_scholar'])} results")
print(f"arXiv: {len(all_results['arxiv'])} results")
```

## Benefits

1. **Fewer API calls**: Get complete information in one request
2. **Better data**: Access to citation metrics, PDF links, and formatted authors
3. **Flexibility**: Search multiple databases or use advanced filters
4. **Convenience**: Auto-detect paper identifiers and formatted output
5. **Backward compatible**: Existing code continues to work

## Technical Implementation

### Code Architecture
- Uses `_impl` suffix pattern for implementation functions
- MCP tool functions are thin async wrappers
- Clean separation between protocol handling and business logic
- All functions properly handle async/await flow

### Deployment Notes
- Service is deployed on Render.com
- Auto-deploys from GitHub repository
- Environment variables required for API keys
- Free tier may sleep after 15 minutes of inactivity