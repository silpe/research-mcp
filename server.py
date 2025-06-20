# -----------------------------------------------------------
# server_enhanced.py – Enhanced ResearchHub MCP with full BioMCP functionality
# -----------------------------------------------------------
from fastmcp import FastMCP
import os, requests, requests.auth, time
import secrets
from typing import Optional, List, Dict, Any, Union
import xml.etree.ElementTree as ET
from datetime import datetime
import json

mcp = FastMCP("ResearchHub")

# ---------- Authentication --------------------------------------------
MCP_AUTH_TOKEN = os.getenv("MCP_AUTH_TOKEN")

# Middleware to check authentication
@mcp.middleware
async def auth_middleware(ctx, call_next):
    """Check authentication token in headers"""
    if MCP_AUTH_TOKEN:
        # Get the authorization header
        auth_header = ctx.request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise Exception("Missing or invalid Authorization header")
        
        token = auth_header.replace("Bearer ", "")
        if not secrets.compare_digest(token, MCP_AUTH_TOKEN):
            raise Exception("Invalid authentication token")
    
    return await call_next(ctx)

# ---------- Enhanced PubMed --------------------------------------------
NCBI_KEY = os.getenv("NCBI_API_KEY")

@mcp.tool
def pubmed_search(query: str, max_results: int = 20, return_details: bool = True):
    """Search PubMed and return article details.
    
    Args:
        query: Search query
        max_results: Maximum number of results
        return_details: If True, returns full article details; if False, returns only PMIDs
    
    Returns:
        List of article details with title, authors, journal, year, and abstract
    """
    # First, search for PMIDs
    url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    params = dict(db="pubmed", term=query, retmax=max_results,
                  retmode="json", api_key=NCBI_KEY)
    r = requests.get(url, params=params, timeout=30)
    r.raise_for_status()
    
    pmids = r.json()["esearchresult"]["idlist"]
    
    if not return_details or not pmids:
        return pmids
    
    # Fetch details for the PMIDs
    articles_dict = pubmed_fetch(pmids)
    
    # Convert to list format with consistent ordering
    articles_list = []
    for pmid in pmids:
        if pmid in articles_dict:
            article = articles_dict[pmid]
            articles_list.append({
                "pmid": pmid,
                "title": article["title"],
                "authors": article["authors"],
                "author_list": ", ".join(article["authors"][:3]) + (" et al." if len(article["authors"]) > 3 else ""),
                "journal": article["journal"],
                "year": article["year"],
                "doi": article["doi"],
                "abstract": article["abstract"],
                "keywords": article["keywords"]
            })
    
    return articles_list

@mcp.tool
def pubmed_fetch(pmids: List[str], format: str = "abstract") -> Dict[str, Any]:
    """Fetch full article details for given PubMed IDs.
    
    Args:
        pmids: List of PubMed IDs
        format: 'abstract' for summary or 'full' for complete record
    
    Returns:
        Dictionary with article details
    """
    if not pmids:
        return {}
    
    # Join PMIDs for batch fetch
    id_str = ",".join(pmids[:10])  # Limit to 10 articles at once
    
    url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
    params = {
        "db": "pubmed",
        "id": id_str,
        "retmode": "xml",
        "api_key": NCBI_KEY
    }
    
    r = requests.get(url, params=params, timeout=30)
    r.raise_for_status()
    
    # Parse XML response
    root = ET.fromstring(r.content)
    articles = {}
    
    for article in root.findall(".//PubmedArticle"):
        pmid = article.find(".//PMID").text
        
        # Extract article details
        article_data = {
            "pmid": pmid,
            "title": article.find(".//ArticleTitle").text,
            "abstract": "",
            "authors": [],
            "journal": "",
            "year": "",
            "doi": "",
            "keywords": []
        }
        
        # Abstract
        abstract_elem = article.find(".//Abstract/AbstractText")
        if abstract_elem is not None:
            article_data["abstract"] = abstract_elem.text
        
        # Authors
        for author in article.findall(".//Author"):
            last_name = author.find("LastName")
            fore_name = author.find("ForeName")
            if last_name is not None and fore_name is not None:
                article_data["authors"].append(f"{fore_name.text} {last_name.text}")
        
        # Journal info
        journal = article.find(".//Journal/Title")
        if journal is not None:
            article_data["journal"] = journal.text
            
        # Publication year
        year = article.find(".//PubDate/Year")
        if year is not None:
            article_data["year"] = year.text
        
        # DOI
        for id_elem in article.findall(".//ArticleId"):
            if id_elem.get("IdType") == "doi":
                article_data["doi"] = id_elem.text
                
        # Keywords
        for keyword in article.findall(".//Keyword"):
            if keyword.text:
                article_data["keywords"].append(keyword.text)
        
        articles[pmid] = article_data
    
    return articles

@mcp.tool
def pubmed_summary(pmids: List[str]) -> List[Dict[str, str]]:
    """Get concise summaries for PubMed articles."""
    articles = pubmed_fetch(pmids, format="abstract")
    
    summaries = []
    for pmid, data in articles.items():
        summary = {
            "pmid": pmid,
            "title": data["title"],
            "authors": ", ".join(data["authors"][:3]) + (" et al." if len(data["authors"]) > 3 else ""),
            "journal": f"{data['journal']} ({data['year']})",
            "abstract_snippet": data["abstract"][:200] + "..." if len(data["abstract"]) > 200 else data["abstract"]
        }
        summaries.append(summary)
    
    return summaries

# ---------- Enhanced Semantic Scholar ----------------------------------
S2_KEY = os.getenv("S2_API_KEY")
RATE_LIMIT = 1

_last_call = 0.0
def _respect_rate_limit():
    global _last_call
    wait = 1.0 / RATE_LIMIT - (time.time() - _last_call)
    if wait > 0:
        time.sleep(wait)
    _last_call = time.time()

@mcp.tool
def semantic_scholar_search(query: str, limit: int = 20, year_range: Optional[str] = None, 
                          min_citations: Optional[int] = None, fields_of_study: Optional[List[str]] = None) -> list[dict]:
    """Search Semantic Scholar for papers with enhanced filtering.
    
    Args:
        query: Search query
        limit: Maximum number of results
        year_range: Year range (e.g., "2020-2024" or "2023")
        min_citations: Minimum citation count filter
        fields_of_study: List of fields to filter by
    
    Returns:
        List of papers with title, authors, year, citations, and more
    """
    _respect_rate_limit()
    url = "https://api.semanticscholar.org/graph/v1/paper/search"
    
    # Enhanced fields including more metadata
    fields = "paperId,title,year,url,authors,abstract,citationCount,influentialCitationCount,venue,journal,publicationTypes,publicationDate,openAccessPdf,fieldsOfStudy,s2FieldsOfStudy"
    
    params = dict(query=query, limit=limit, fields=fields)
    
    # Add year filter if provided
    if year_range:
        params["year"] = year_range
    
    # Add fields of study filter if provided
    if fields_of_study:
        params["fieldsOfStudy"] = ",".join(fields_of_study)
    
    headers = {"x-api-key": S2_KEY} if S2_KEY else {}
    r = requests.get(url, params=params, headers=headers, timeout=30)
    r.raise_for_status()
    
    papers = r.json().get("data", [])
    
    # Apply additional filters if needed
    if min_citations is not None:
        papers = [p for p in papers if (p.get("citationCount") or 0) >= min_citations]
    
    # Enhance paper data for easier consumption
    enhanced_papers = []
    for paper in papers:
        enhanced = {
            **paper,
            # Add formatted author list
            "author_names": [a.get("name", "Unknown") for a in (paper.get("authors") or [])],
            "author_list": ", ".join([a.get("name", "Unknown") for a in (paper.get("authors") or [])[:3]]) + 
                          (" et al." if len(paper.get("authors", [])) > 3 else ""),
            # Add venue info
            "venue_info": paper.get("venue") or paper.get("journal", {}).get("name") if isinstance(paper.get("journal"), dict) else paper.get("journal"),
            # Add open access info
            "has_pdf": bool(paper.get("openAccessPdf")),
            "pdf_url": paper.get("openAccessPdf", {}).get("url") if paper.get("openAccessPdf") else None,
            # Add publication info
            "pub_date": paper.get("publicationDate") or str(paper.get("year", "Unknown")),
            # Add citation metrics
            "citation_metrics": {
                "total": paper.get("citationCount", 0),
                "influential": paper.get("influentialCitationCount", 0)
            }
        }
        enhanced_papers.append(enhanced)
    
    return enhanced_papers

@mcp.tool
def semantic_scholar_paper_details(paper_id: str) -> dict:
    """Get detailed information about a specific paper.
    
    Args:
        paper_id: S2 paper ID or DOI
    
    Returns:
        Detailed paper information including citations, references, etc.
    """
    _respect_rate_limit()
    url = f"https://api.semanticscholar.org/graph/v1/paper/{paper_id}"
    fields = "paperId,title,abstract,year,authors,citationCount,referenceCount,influentialCitationCount,fieldsOfStudy,s2FieldsOfStudy,publicationTypes,journal,venue,externalIds,openAccessPdf,publicationDate,citationsPerYear,url"
    params = {"fields": fields}
    headers = {"x-api-key": S2_KEY} if S2_KEY else {}
    
    r = requests.get(url, params=params, headers=headers, timeout=30)
    r.raise_for_status()
    
    paper = r.json()
    
    # Enhance the paper details
    enhanced = {
        **paper,
        # Add formatted author list
        "author_names": [a.get("name", "Unknown") for a in (paper.get("authors") or [])],
        "author_list": ", ".join([a.get("name", "Unknown") for a in (paper.get("authors") or [])[:3]]) + 
                      (" et al." if len(paper.get("authors", [])) > 3 else ""),
        # Add venue info
        "venue_info": paper.get("venue") or (paper.get("journal", {}).get("name") if isinstance(paper.get("journal"), dict) else paper.get("journal")),
        # Add open access info
        "has_pdf": bool(paper.get("openAccessPdf")),
        "pdf_url": paper.get("openAccessPdf", {}).get("url") if paper.get("openAccessPdf") else None,
        # Add DOI
        "doi": paper.get("externalIds", {}).get("DOI") if paper.get("externalIds") else None,
        # Add arXiv ID
        "arxiv_id": paper.get("externalIds", {}).get("ArXiv") if paper.get("externalIds") else None,
        # Enhanced citation metrics
        "citation_metrics": {
            "total": paper.get("citationCount", 0),
            "influential": paper.get("influentialCitationCount", 0),
            "yearly": paper.get("citationsPerYear", {})
        }
    }
    
    return enhanced

@mcp.tool
def semantic_scholar_citations(paper_id: str, limit: int = 20) -> list[dict]:
    """Get papers that cite the given paper."""
    _respect_rate_limit()
    url = f"https://api.semanticscholar.org/graph/v1/paper/{paper_id}/citations"
    params = {
        "fields": "title,year,authors,abstract,citationCount",
        "limit": limit
    }
    headers = {"x-api-key": S2_KEY} if S2_KEY else {}
    
    r = requests.get(url, params=params, headers=headers, timeout=30)
    r.raise_for_status()
    return r.json().get("data", [])

@mcp.tool
def semantic_scholar_references(paper_id: str, limit: int = 20) -> list[dict]:
    """Get papers referenced by the given paper."""
    _respect_rate_limit()
    url = f"https://api.semanticscholar.org/graph/v1/paper/{paper_id}/references"
    params = {
        "fields": "title,year,authors,abstract,citationCount",
        "limit": limit
    }
    headers = {"x-api-key": S2_KEY} if S2_KEY else {}
    
    r = requests.get(url, params=params, headers=headers, timeout=30)
    r.raise_for_status()
    return r.json().get("data", [])

@mcp.tool
def semantic_scholar_author_search(author_name: str, limit: int = 10) -> list[dict]:
    """Search for authors by name."""
    _respect_rate_limit()
    url = "https://api.semanticscholar.org/graph/v1/author/search"
    params = {
        "query": author_name,
        "limit": limit
    }
    headers = {"x-api-key": S2_KEY} if S2_KEY else {}
    
    r = requests.get(url, params=params, headers=headers, timeout=30)
    r.raise_for_status()
    return r.json().get("data", [])

@mcp.tool
def semantic_scholar_author_papers(author_id: str, limit: int = 20) -> list[dict]:
    """Get papers by a specific author."""
    _respect_rate_limit()
    url = f"https://api.semanticscholar.org/graph/v1/author/{author_id}/papers"
    params = {
        "fields": "title,year,abstract,citationCount,journal",
        "limit": limit
    }
    headers = {"x-api-key": S2_KEY} if S2_KEY else {}
    
    r = requests.get(url, params=params, headers=headers, timeout=30)
    r.raise_for_status()
    return r.json().get("data", [])

# ---------- Enhanced Reddit --------------------------------------------
REDDIT_ID     = os.getenv("REDDIT_CLIENT_ID")
REDDIT_SECRET = os.getenv("REDDIT_CLIENT_SECRET")
USER_AGENT    = "research-mcp-enhanced/0.2 (enhanced research tools)"

def _reddit_token() -> str:
    auth = requests.auth.HTTPBasicAuth(REDDIT_ID, REDDIT_SECRET)
    r = requests.post("https://www.reddit.com/api/v1/access_token",
                      auth=auth,
                      data={"grant_type": "client_credentials"},
                      headers={"User-Agent": USER_AGENT},
                      timeout=30)
    r.raise_for_status()
    return r.json()["access_token"]

@mcp.tool
def reddit_search(query: str, limit: int = 20, sort: str = "new", search_type: str = "link") -> list[dict]:
    """Search Reddit submissions.
    
    Args:
        query: Search query
        limit: Number of results
        sort: Sort order (new, hot, top, relevance)
        search_type: Type of content (link, self, all)
    """
    headers = {"User-Agent": USER_AGENT,
               "Authorization": f"Bearer {_reddit_token()}"}
    params = dict(q=query, limit=limit, sort=sort)
    
    if search_type != "all":
        params["type"] = search_type
        
    r = requests.get("https://oauth.reddit.com/search",
                     headers=headers, params=params, timeout=30)
    r.raise_for_status()
    return [c["data"] for c in r.json()["data"]["children"]]

@mcp.tool
def reddit_subreddit_search(subreddit: str, query: str, limit: int = 20, sort: str = "new") -> list[dict]:
    """Search within a specific subreddit."""
    headers = {"User-Agent": USER_AGENT,
               "Authorization": f"Bearer {_reddit_token()}"}
    params = dict(q=query, limit=limit, sort=sort, restrict_sr="true")
    
    r = requests.get(f"https://oauth.reddit.com/r/{subreddit}/search",
                     headers=headers, params=params, timeout=30)
    r.raise_for_status()
    return [c["data"] for c in r.json()["data"]["children"]]

@mcp.tool
def reddit_comments(submission_id: str, limit: int = 50) -> dict:
    """Get comments for a specific Reddit submission.
    
    Args:
        submission_id: Reddit submission ID (without 't3_' prefix)
        limit: Maximum number of comments to retrieve
    """
    headers = {"User-Agent": USER_AGENT,
               "Authorization": f"Bearer {_reddit_token()}"}
    params = {"limit": limit}
    
    r = requests.get(f"https://oauth.reddit.com/comments/{submission_id}",
                     headers=headers, params=params, timeout=30)
    r.raise_for_status()
    
    data = r.json()
    submission = data[0]["data"]["children"][0]["data"]
    comments = []
    
    def extract_comments(comment_data):
        for item in comment_data:
            if item["kind"] == "t1":  # Comment
                comment = item["data"]
                comments.append({
                    "author": comment.get("author"),
                    "body": comment.get("body"),
                    "score": comment.get("score"),
                    "created_utc": comment.get("created_utc"),
                    "id": comment.get("id")
                })
                
                # Process nested replies
                if comment.get("replies") and isinstance(comment["replies"], dict):
                    extract_comments(comment["replies"]["data"]["children"])
    
    if len(data) > 1:
        extract_comments(data[1]["data"]["children"])
    
    return {
        "submission": {
            "title": submission.get("title"),
            "author": submission.get("author"),
            "score": submission.get("score"),
            "url": submission.get("url"),
            "selftext": submission.get("selftext")
        },
        "comments": comments
    }

# ---------- arXiv Integration ------------------------------------------
@mcp.tool
def arxiv_search(query: str, max_results: int = 20, sort_by: str = "relevance") -> list[dict]:
    """Search arXiv for papers.
    
    Args:
        query: Search query (supports arXiv query syntax)
        max_results: Maximum number of results
        sort_by: Sort order (relevance, lastUpdatedDate, submittedDate)
    """
    url = "http://export.arxiv.org/api/query"
    params = {
        "search_query": query,
        "max_results": max_results,
        "sortBy": sort_by,
        "sortOrder": "descending"
    }
    
    r = requests.get(url, params=params, timeout=30)
    r.raise_for_status()
    
    # Parse XML response
    root = ET.fromstring(r.content)
    
    # Define namespaces
    ns = {
        'atom': 'http://www.w3.org/2005/Atom',
        'arxiv': 'http://arxiv.org/schemas/atom'
    }
    
    papers = []
    for entry in root.findall('atom:entry', ns):
        paper = {
            "id": entry.find('atom:id', ns).text.split('/')[-1],
            "title": entry.find('atom:title', ns).text.strip(),
            "summary": entry.find('atom:summary', ns).text.strip(),
            "authors": [author.find('atom:name', ns).text for author in entry.findall('atom:author', ns)],
            "published": entry.find('atom:published', ns).text,
            "updated": entry.find('atom:updated', ns).text,
            "categories": [cat.get('term') for cat in entry.findall('arxiv:category', ns)],
            "pdf_url": None,
            "doi": None
        }
        
        # Find PDF link
        for link in entry.findall('atom:link', ns):
            if link.get('type') == 'application/pdf':
                paper["pdf_url"] = link.get('href')
        
        # Find DOI if available
        doi_elem = entry.find('arxiv:doi', ns)
        if doi_elem is not None:
            paper["doi"] = doi_elem.text
        
        papers.append(paper)
    
    return papers

@mcp.tool
def arxiv_paper(arxiv_id: str) -> dict:
    """Get details for a specific arXiv paper by ID."""
    return arxiv_search(f"id:{arxiv_id}", max_results=1)[0]

# ---------- CrossRef Integration ---------------------------------------
@mcp.tool
def crossref_works_search(query: str, rows: int = 20, filter_dict: Optional[Dict[str, str]] = None) -> dict:
    """Search CrossRef for scholarly works.
    
    Args:
        query: Search query
        rows: Number of results
        filter_dict: Optional filters (e.g., {"from-pub-date": "2020-01-01"})
    """
    url = "https://api.crossref.org/works"
    params = {
        "query": query,
        "rows": rows
    }
    
    # Add filters if provided
    if filter_dict:
        filter_parts = [f"{k}:{v}" for k, v in filter_dict.items()]
        params["filter"] = ",".join(filter_parts)
    
    headers = {"User-Agent": USER_AGENT}
    r = requests.get(url, params=params, headers=headers, timeout=30)
    r.raise_for_status()
    
    data = r.json()
    return {
        "total_results": data["message"]["total-results"],
        "items": data["message"]["items"]
    }

@mcp.tool
def crossref_doi_lookup(doi: str) -> dict:
    """Look up a specific work by DOI in CrossRef."""
    url = f"https://api.crossref.org/works/{doi}"
    headers = {"User-Agent": USER_AGENT}
    
    r = requests.get(url, headers=headers, timeout=30)
    r.raise_for_status()
    
    return r.json()["message"]

@mcp.tool
def crossref_journal_works(issn: str, rows: int = 20) -> dict:
    """Get recent works from a specific journal by ISSN."""
    url = f"https://api.crossref.org/journals/{issn}/works"
    params = {"rows": rows}
    headers = {"User-Agent": USER_AGENT}
    
    r = requests.get(url, params=params, headers=headers, timeout=30)
    r.raise_for_status()
    
    data = r.json()
    return {
        "journal_title": data["message"].get("title"),
        "total_results": data["message"]["total-results"],
        "items": data["message"]["items"]
    }

# ---------- Combined Search Functions ----------------------------------
@mcp.tool
def multi_database_search(query: str, databases: Optional[List[str]] = None, max_results_per_db: int = 10) -> Dict[str, List[Dict[str, Any]]]:
    """Search multiple academic databases simultaneously.
    
    Args:
        query: Search query
        databases: List of databases to search (default: all available)
                  Options: ["pubmed", "semantic_scholar", "arxiv", "crossref"]
        max_results_per_db: Maximum results per database
    
    Returns:
        Dictionary with results from each database
    """
    if databases is None:
        databases = ["pubmed", "semantic_scholar", "arxiv", "crossref"]
    
    results = {}
    
    # Search each database
    if "pubmed" in databases:
        try:
            results["pubmed"] = pubmed_search(query, max_results=max_results_per_db, return_details=True)
        except Exception as e:
            results["pubmed_error"] = str(e)
    
    if "semantic_scholar" in databases:
        try:
            results["semantic_scholar"] = semantic_scholar_search(query, limit=max_results_per_db)
        except Exception as e:
            results["semantic_scholar_error"] = str(e)
    
    if "arxiv" in databases:
        try:
            results["arxiv"] = arxiv_search(query, max_results=max_results_per_db)
        except Exception as e:
            results["arxiv_error"] = str(e)
    
    if "crossref" in databases:
        try:
            crossref_result = crossref_works_search(query, rows=max_results_per_db)
            results["crossref"] = crossref_result.get("items", [])
        except Exception as e:
            results["crossref_error"] = str(e)
    
    return results

@mcp.tool
def get_paper_by_identifier(identifier: str, id_type: Optional[str] = None) -> Dict[str, Any]:
    """Get paper details using any identifier (DOI, PMID, arXiv ID, S2 ID).
    
    Args:
        identifier: Paper identifier
        id_type: Type of identifier (doi, pmid, arxiv, s2). If None, will try to auto-detect.
    
    Returns:
        Paper details from the appropriate database
    """
    # Auto-detect identifier type if not specified
    if id_type is None:
        if identifier.startswith("10.") and "/" in identifier:
            id_type = "doi"
        elif identifier.isdigit() and len(identifier) >= 7:
            id_type = "pmid"
        elif "." in identifier and any(char.isdigit() for char in identifier):
            id_type = "arxiv"
        else:
            id_type = "s2"
    
    try:
        if id_type == "doi":
            # Try CrossRef first for DOI
            crossref_data = crossref_doi_lookup(identifier)
            # Also try Semantic Scholar
            try:
                s2_data = semantic_scholar_paper_details(identifier)
                # Merge data
                return {
                    "source": "crossref+semantic_scholar",
                    "crossref": crossref_data,
                    "semantic_scholar": s2_data
                }
            except:
                return {"source": "crossref", **crossref_data}
        
        elif id_type == "pmid":
            # Fetch from PubMed
            articles = pubmed_fetch([identifier])
            if identifier in articles:
                return {"source": "pubmed", **articles[identifier]}
            else:
                raise ValueError(f"PMID {identifier} not found")
        
        elif id_type == "arxiv":
            # Fetch from arXiv
            paper = arxiv_paper(identifier)
            return {"source": "arxiv", **paper}
        
        elif id_type == "s2":
            # Fetch from Semantic Scholar
            paper = semantic_scholar_paper_details(identifier)
            return {"source": "semantic_scholar", **paper}
        
        else:
            raise ValueError(f"Unknown identifier type: {id_type}")
    
    except Exception as e:
        return {"error": str(e), "identifier": identifier, "id_type": id_type}

# ---------- Entrypoint -------------------------------------------------
app = mcp.http_app()  # Create the HTTP app for uvicorn

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))