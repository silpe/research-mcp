# ResearchHub MCP - Quick Reference

## Most Common Operations

### Search All Databases
```python
# Search everything at once
results = multi_database_search("your search query")
```

### Get Paper by DOI/PMID/arXiv ID
```python
# Works with any identifier
paper = get_paper_by_identifier("10.1038/nature12373")  # DOI
paper = get_paper_by_identifier("32501203")              # PMID  
paper = get_paper_by_identifier("2301.08727")            # arXiv
```

### PubMed Search (Full Details)
```python
# Get complete article info by default
articles = pubmed_search("CRISPR", max_results=10)
```

### Semantic Scholar with Filters
```python
# Recent, highly-cited papers only
papers = semantic_scholar_search(
    "machine learning",
    year_range="2022-2024",
    min_citations=50
)
```

### Get Citation Network
```python
# Papers citing this work
citations = semantic_scholar_citations("paper_id")

# Papers this work references
references = semantic_scholar_references("paper_id")
```

## Implementation Notes

When calling from inside the codebase (not through MCP):
- Use `pubmed_search_impl()` not `pubmed_search()`
- Use `semantic_scholar_search_impl()` not `semantic_scholar_search()`
- etc.

The `@mcp.tool` decorator makes functions non-callable from Python!