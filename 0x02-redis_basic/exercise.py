#!/usr/bin/env python3
"""
This module defines a Cache class to interact with a Redis database.
"""

import redis
import uuid
from typing import Union


class Cache:
    """
    Cache class for storing data in Redis with a random key.
    """

    def __init__(self):
        """
        Initialize the Cache instance with a Redis client and flush the database.
        """
        self._redis = redis.Redis()
        self._redis.flushdb()

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

