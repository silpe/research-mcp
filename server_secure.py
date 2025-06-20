# -----------------------------------------------------------
# server_secure.py  – ResearchHub MCP with Authentication
# -----------------------------------------------------------
from fastmcp import FastMCP
import os, requests, requests.auth, time
from typing import Optional
import secrets

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

# ---------- PubMed ----------------------------------------------------
NCBI_KEY = os.getenv("NCBI_API_KEY")

@mcp.tool
def pubmed_search(query: str, max_results: int = 20) -> list[str]:
    """Return PubMed IDs that match the search term."""
    url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    params = dict(db="pubmed", term=query, retmax=max_results,
                  retmode="json", api_key=NCBI_KEY)
    r = requests.get(url, params=params, timeout=30)
    r.raise_for_status()
    return r.json()["esearchresult"]["idlist"]

# ---------- Semantic Scholar ------------------------------------------
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
def semantic_scholar_search(query: str, limit: int = 20) -> list[dict]:
    """Return title, year, url for papers matching `query` (S2)."""
    _respect_rate_limit()
    url = "https://api.semanticscholar.org/graph/v1/paper/search"
    params = dict(query=query, limit=limit, fields="title,year,url")
    headers = {"x-api-key": S2_KEY}
    r = requests.get(url, params=params, headers=headers, timeout=30)
    r.raise_for_status()
    return r.json().get("data", [])

# ---------- Reddit -----------------------------------------------------
REDDIT_ID     = os.getenv("REDDIT_CLIENT_ID")
REDDIT_SECRET = os.getenv("REDDIT_CLIENT_SECRET")
USER_AGENT    = "research-mcp/0.1 (contact: you@example.com)"

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
def reddit_search(query: str, limit: int = 20, sort: str = "new") -> list[dict]:
    """Search Reddit submissions (links only)."""
    headers = {"User-Agent": USER_AGENT,
               "Authorization": f"Bearer {_reddit_token()}"}
    params = dict(q=query, limit=limit, sort=sort, type="link")
    r = requests.get("https://oauth.reddit.com/search",
                     headers=headers, params=params, timeout=30)
    r.raise_for_status()
    return [c["data"] for c in r.json()["data"]["children"]]

# ---------- Entrypoint -------------------------------------------------
app = mcp.http_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))