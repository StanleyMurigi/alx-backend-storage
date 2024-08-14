#!/usr/bin/env python3
"""
This module defines a Cache class to interact with a Redis database and a count_calls decorator to count method calls.
"""

import redis
import uuid
from typing import Union, Callable, Optional
from functools import wraps


def count_calls(method: Callable) -> Callable:
    """
    Decorator that counts the number of times a method is called.
    
    Args:
        method (Callable): The method to be decorated.
    
    Returns:
        Callable: The decorated method that increments the call count.
    """
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        """
        Wrapper function to increment the call count in Redis.
        """
        # Increment the count for the method's qualified name
        self._redis.incr(method.__qualname__)
        # Call the original method
        return method(self, *args, **kwargs)
    
    return wrapper


class Cache:
    """
    Cache class for storing and retrieving data in Redis.
    """

    def __init__(self):
        """
        Initialize the Cache instance with a Redis client and flush the database.
        """
        self._redis = redis.Redis()
        self._redis.flushdb()

    @count_calls
    def store(self, data: Union[str, bytes, int, float]) -> str:
        """
        Store the given data in Redis with a randomly generated key.
        
        Args:
            data (Union[str, bytes, int, float]): The data to be stored in Redis.
        
        Returns:
            str: The key under which the data is stored.
        """
        key = str(uuid.uuid4())
        self._redis.set(key, data)
        return key

    def get(self, key: str, fn: Optional[Callable] = None) -> Union[str, bytes, int, float, None]:
        """
        Retrieve data from Redis and optionally apply a conversion function.
        
        Args:
            key (str): The key of the data to retrieve.
            fn (Optional[Callable]): A function to apply to the data to convert it to the desired format.
        
        Returns:
            Union[str, bytes, int, float, None]: The data from Redis, optionally converted by fn.
        """
        data = self._redis.get(key)
        if data is not None and fn is not None:
            return fn(data)
        return data

    def get_str(self, key: str) -> Optional[str]:
        """
        Retrieve data from Redis and convert it to a string.
        
        Args:
            key (str): The key of the data to retrieve.
        
        Returns:
            Optional[str]: The data converted to a string, or None if the key doesn't exist.
        """
        return self.get(key, fn=lambda d: d.decode('utf-8'))

    def get_int(self, key: str) -> Optional[int]:
        """
        Retrieve data from Redis and convert it to an integer.
        
        Args:
            key (str): The key of the data to retrieve.
        
        Returns:
            Optional[int]: The data converted to an integer, or None if the key doesn't exist.
        """
        return self.get(key, fn=int)

