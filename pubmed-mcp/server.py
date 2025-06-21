# -----------------------------------------------------------
# PubMed MCP Service - PubMed search and retrieval
# -----------------------------------------------------------
from fastmcp import FastMCP
import os, requests, requests.auth, time
import secrets
from typing import Optional, List, Dict, Any, Union
import xml.etree.ElementTree as ET
from datetime import datetime
import json

mcp = FastMCP("PubMed")

# ---------- Authentication --------------------------------------------
MCP_AUTH_TOKEN = os.getenv("MCP_AUTH_TOKEN")

# Note: Authentication is handled by the MCP client configuration
# The MCP_AUTH_TOKEN is used when registering the server with Claude

# ---------- Enhanced PubMed --------------------------------------------
NCBI_KEY = os.getenv("NCBI_API_KEY")

def _pubmed_search_impl(query: str, max_results: int = 20, return_details: bool = True):
    """Internal implementation for PubMed search."""
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
    articles_dict = _pubmed_fetch_impl(pmids)
    
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

def _pubmed_fetch_impl(pmids: List[str], format: str = "abstract") -> Dict[str, Any]:
    """Internal implementation for fetching PubMed article details."""
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
        pmid_elem = article.find(".//PMID")
        if pmid_elem is None:
            continue
        pmid = pmid_elem.text
        
        # Extract article details
        title_elem = article.find(".//ArticleTitle")
        article_data = {
            "pmid": pmid,
            "title": title_elem.text if title_elem is not None else "",
            "abstract": "",
            "authors": [],
            "journal": "",
            "year": "",
            "doi": "",
            "keywords": []
        }
        
        # Abstract
        abstract_elem = article.find(".//Abstract/AbstractText")
        if abstract_elem is not None and abstract_elem.text:
            article_data["abstract"] = abstract_elem.text
        
        # Authors
        for author in article.findall(".//Author"):
            last_name = author.find("LastName")
            fore_name = author.find("ForeName")
            if last_name is not None and fore_name is not None and last_name.text and fore_name.text:
                article_data["authors"].append(f"{fore_name.text} {last_name.text}")
        
        # Journal info
        journal = article.find(".//Journal/Title")
        if journal is not None and journal.text:
            article_data["journal"] = journal.text
            
        # Publication year
        year = article.find(".//PubDate/Year")
        if year is not None and year.text:
            article_data["year"] = year.text
        
        # DOI
        for id_elem in article.findall(".//ArticleId"):
            if id_elem.get("IdType") == "doi" and id_elem.text:
                article_data["doi"] = id_elem.text
                
        # Keywords
        for keyword in article.findall(".//Keyword"):
            if keyword.text:
                article_data["keywords"].append(keyword.text)
        
        articles[pmid] = article_data
    
    return articles

def _pubmed_summary_impl(pmids: List[str]) -> List[Dict[str, str]]:
    """Internal implementation for PubMed summaries."""
    articles = _pubmed_fetch_impl(pmids, format="abstract")
    
    summaries = []
    for pmid, data in articles.items():
        abstract = data.get("abstract", "")
        summary = {
            "pmid": pmid,
            "title": data.get("title", ""),
            "authors": ", ".join(data.get("authors", [])[:3]) + (" et al." if len(data.get("authors", [])) > 3 else ""),
            "journal": f"{data.get('journal', '')} ({data.get('year', '')})",
            "abstract_snippet": abstract[:200] + "..." if len(abstract) > 200 else abstract
        }
        summaries.append(summary)
    
    return summaries

# MCP Tool Definitions - These wrap the implementation functions
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
    return _pubmed_search_impl(query, max_results, return_details)

@mcp.tool
def pubmed_fetch(pmids: List[str], format: str = "abstract") -> Dict[str, Any]:
    """Fetch full article details for given PubMed IDs.
    
    Args:
        pmids: List of PubMed IDs
        format: 'abstract' for summary or 'full' for complete record
    
    Returns:
        Dictionary with article details
    """
    return _pubmed_fetch_impl(pmids, format)

@mcp.tool
def pubmed_summary(pmids: List[str]) -> List[Dict[str, str]]:
    """Get concise summaries for PubMed articles."""
    return _pubmed_summary_impl(pmids)

# ---------- Entrypoint -------------------------------------------------
app = mcp.http_app()  # Create the HTTP app for uvicorn

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))