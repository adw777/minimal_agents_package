"""Web search tool implementation."""

import os
import requests
from typing import Dict, Optional, List

from minimal_agents.tools.base import Tool

class WebSearch(Tool):
    """Tool for searching the web for information."""
    
    name: str = "Web Search"
    description: str = (
        "Search the web for current information. "
        "Input should be a search query or specific question. "
        "Results will include relevant snippets from web pages."
    )
    api_key: Optional[str] = None
    search_engine: str = "serp"  # Options: "serp", "google", "bing"
    max_results: int = 5
    
    def __init__(
        self, 
        api_key: Optional[str] = None,
        search_engine: str = "serp",
        max_results: int = 5,
        **data
    ):
        """Initialize web search tool.
        
        Args:
            api_key: API key for the search service (defaults to SEARCH_API_KEY env var)
            search_engine: Which search engine to use (serp, google, bing)
            max_results: Maximum number of results to return
        """
        super().__init__(**data)
        self.api_key = api_key or os.environ.get("SEARCH_API_KEY")
        self.search_engine = search_engine
        self.max_results = max_results
        
        if not self.api_key:
            raise ValueError("Search API key is required. Set SEARCH_API_KEY environment variable or pass api_key.")
    
    def run(self, input_text: str) -> str:
        """Run a web search with the given query.
        
        Args:
            input_text: Search query or question
            
        Returns:
            Search results as formatted string
        """
        query = input_text.strip()
        
        try:
            if self.search_engine == "serp":
                results = self._search_with_serp(query)
            elif self.search_engine == "google":
                results = self._search_with_google(query)
            elif self.search_engine == "bing":
                results = self._search_with_bing(query)
            else:
                return f"Error: Unsupported search engine '{self.search_engine}'"
                
            return self._format_results(query, results)
        except Exception as e:
            return f"Search error: {str(e)}"
    
    def _search_with_serp(self, query: str) -> List[Dict]:
        """Perform search with SerpAPI.
        
        Args:
            query: Search query
            
        Returns:
            List of result dictionaries
        """
        url = "https://serpapi.com/search"
        params = {
            "q": query,
            "api_key": self.api_key,
            "engine": "google",
            "num": self.max_results
        }
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        results = []
        if "organic_results" in data:
            for result in data["organic_results"][:self.max_results]:
                results.append({
                    "title": result.get("title", "No title"),
                    "snippet": result.get("snippet", "No snippet available"),
                    "url": result.get("link", "#")
                })
        
        return results
    
    def _search_with_google(self, query: str) -> List[Dict]:
        """Perform search with Google Custom Search API.
        
        Args:
            query: Search query
            
        Returns:
            List of result dictionaries
        """
        # Requires additional environment variables:
        # - GOOGLE_CSE_ID (Custom Search Engine ID)
        cse_id = os.environ.get("GOOGLE_CSE_ID")
        if not cse_id:
            raise ValueError("GOOGLE_CSE_ID environment variable is required for Google search")
            
        url = "https://www.googleapis.com/customsearch/v1"
        params = {
            "q": query,
            "key": self.api_key,
            "cx": cse_id,
            "num": self.max_results
        }
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        results = []
        if "items" in data:
            for item in data["items"][:self.max_results]:
                results.append({
                    "title": item.get("title", "No title"),
                    "snippet": item.get("snippet", "No snippet available"),
                    "url": item.get("link", "#")
                })
        
        return results
    
    def _search_with_bing(self, query: str) -> List[Dict]:
        """Perform search with Bing Search API.
        
        Args:
            query: Search query
            
        Returns:
            List of result dictionaries
        """
        url = "https://api.bing.microsoft.com/v7.0/search"
        headers = {"Ocp-Apim-Subscription-Key": self.api_key}
        params = {
            "q": query,
            "count": self.max_results,
            "responseFilter": "Webpages"
        }
        
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        
        results = []
        if "webPages" in data and "value" in data["webPages"]:
            for item in data["webPages"]["value"][:self.max_results]:
                results.append({
                    "title": item.get("name", "No title"),
                    "snippet": item.get("snippet", "No snippet available"),
                    "url": item.get("url", "#")
                })
        
        return results
    
    def _format_results(self, query: str, results: List[Dict]) -> str:
        """Format search results for output.
        
        Args:
            query: Original search query
            results: List of result dictionaries
            
        Returns:
            Formatted search results as string
        """
        if not results:
            return f"No results found for query: {query}"
            
        output = f"Search results for: {query}\n\n"
        
        for i, result in enumerate(results, 1):
            output += f"{i}. {result['title']}\n"
            output += f"   {result['snippet']}\n"
            output += f"   URL: {result['url']}\n\n"
            
        return output