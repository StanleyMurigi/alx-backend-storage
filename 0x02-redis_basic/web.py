#!/usr/bin/env python3
"""
Web cache and tracker implementation using Redis.
"""

import redis
import requests
from typing import Callable
from functools import wraps


# Connect to Redis
r = redis.Redis()

def cache_decorator(method: Callable) -> Callable:
    """
    Decorator to cache the result of the get_page function and track URL access count.
    
    Args:
        method (Callable): The method to be decorated.
    
    Returns:
        Callable: The decorated method with caching and tracking functionality.
    """
    @wraps(method)
    def wrapper(url: str) -> str:
        """
        Wrapper function that implements caching and tracking.
        
        Args:
            url (str): The URL to fetch.
        
        Returns:
            str: The HTML content of the URL.
        """
        # Track the number of times the URL has been accessed
        r.incr(f"count:{url}")
        
        # Check if the URL's content is already cached
        cached_content = r.get(f"cached:{url}")
        if cached_content:
            return cached_content.decode('utf-8')
        
        # Fetch the HTML content
        html_content = method(url)
        
        # Cache the content with an expiration of 10 seconds
        r.setex(f"cached:{url}", 10, html_content)
        
        return html_content
    
    return wrapper

@cache_decorator
def get_page(url: str) -> str:
    """
    Fetch the HTML content of a given URL and return it.
    
    Args:
        url (str): The URL to fetch.
    
    Returns:
        str: The HTML content of the URL.
    """
    response = requests.get(url)
    return response.text

