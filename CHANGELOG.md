# Changelog

## 2025-06-20 - Enhanced Version

### Added
- **PubMed**: `pubmed_fetch` and `pubmed_summary` for full article details
- **Semantic Scholar**: Enhanced search with authors, citations, and paper network tools
- **Reddit**: Subreddit search and comment fetching
- **arXiv**: Full search and paper details
- **CrossRef**: Works search, DOI lookup, and journal publications
- **Security**: Optional MCP authentication via Bearer token

### Changed
- Semantic Scholar search now returns authors, abstract, and citation count
- Reddit search supports content type filtering
- Consolidated documentation into single README.md

### Technical Details
- All original functionality preserved for backward compatibility
- No additional dependencies required
- Deployed to Render.com with automatic GitHub integration
- Rate limiting enforced for API compliance