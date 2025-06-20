#!/usr/bin/env python3
"""Test script for ResearchHub MCP improvements"""

import os
import sys

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the server module
from server import (
    pubmed_search, 
    semantic_scholar_search,
    multi_database_search,
    get_paper_by_identifier
)

def test_pubmed_search():
    """Test enhanced PubMed search"""
    print("\n=== Testing Enhanced PubMed Search ===")
    
    # Test with full details
    results = pubmed_search("CRISPR", max_results=2)
    print(f"Found {len(results)} articles with details")
    
    if results:
        article = results[0]
        print(f"\nFirst article:")
        print(f"  Title: {article['title'][:80]}...")
        print(f"  Authors: {article['author_list']}")
        print(f"  Journal: {article['journal']} ({article['year']})")
        print(f"  Has abstract: {'Yes' if article['abstract'] else 'No'}")
        print(f"  DOI: {article['doi'] or 'N/A'}")

def test_semantic_scholar():
    """Test enhanced Semantic Scholar search"""
    print("\n=== Testing Enhanced Semantic Scholar Search ===")
    
    # Test with filters
    results = semantic_scholar_search(
        "machine learning", 
        limit=3,
        year_range="2023-2024",
        min_citations=10
    )
    
    print(f"Found {len(results)} papers from 2023-2024 with 10+ citations")
    
    if results:
        paper = results[0]
        print(f"\nFirst paper:")
        print(f"  Title: {paper['title'][:80]}...")
        print(f"  Authors: {paper['author_list']}")
        print(f"  Year: {paper['year']}")
        print(f"  Citations: {paper['citation_metrics']['total']} (influential: {paper['citation_metrics']['influential']})")
        print(f"  Has PDF: {'Yes' if paper['has_pdf'] else 'No'}")
        print(f"  Venue: {paper['venue_info'] or 'N/A'}")

def test_multi_search():
    """Test multi-database search"""
    print("\n=== Testing Multi-Database Search ===")
    
    results = multi_database_search(
        "COVID-19 vaccine", 
        databases=["pubmed", "semantic_scholar"],
        max_results_per_db=2
    )
    
    for db, items in results.items():
        if not db.endswith("_error"):
            print(f"\n{db}: {len(items)} results")
            if items and len(items) > 0:
                first = items[0]
                title = first.get('title', 'N/A')
                print(f"  First result: {title[:60]}...")

def test_identifier_lookup():
    """Test paper lookup by identifier"""
    print("\n=== Testing Identifier Lookup ===")
    
    # Test with a DOI
    doi = "10.1038/s41586-020-2649-2"
    print(f"\nLooking up DOI: {doi}")
    result = get_paper_by_identifier(doi)
    
    if "error" not in result:
        print(f"  Source: {result['source']}")
        if 'semantic_scholar' in result:
            s2_data = result['semantic_scholar']
            print(f"  Title: {s2_data.get('title', 'N/A')[:60]}...")
            print(f"  Citation count: {s2_data.get('citation_metrics', {}).get('total', 'N/A')}")

if __name__ == "__main__":
    print("Testing ResearchHub MCP Improvements")
    print("=" * 50)
    
    # Set dummy API keys if not present (for testing structure only)
    if not os.getenv("NCBI_API_KEY"):
        os.environ["NCBI_API_KEY"] = "test_key"
    if not os.getenv("S2_API_KEY"):
        os.environ["S2_API_KEY"] = "test_key"
    
    try:
        test_pubmed_search()
    except Exception as e:
        print(f"PubMed test error: {e}")
    
    try:
        test_semantic_scholar()
    except Exception as e:
        print(f"Semantic Scholar test error: {e}")
    
    try:
        test_multi_search()
    except Exception as e:
        print(f"Multi-search test error: {e}")
    
    try:
        test_identifier_lookup()
    except Exception as e:
        print(f"Identifier lookup test error: {e}")
    
    print("\n" + "=" * 50)
    print("Testing complete!")