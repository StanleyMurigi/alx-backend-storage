#!/usr/bin/env python3
"""
This module defines a Cache class to interact with a Redis database, and decorators to count method calls and store call history. It also includes a replay function to display the history of calls.
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
        self._redis.incr(method.__qualname__)
        return method(self, *args, **kwargs)
    
    return wrapper


def call_history(method: Callable) -> Callable:
    """
    Decorator to store the history of inputs and outputs for a particular function.
    
    Args:
        method (Callable): The method to be decorated.
    
    Returns:
        Callable: The decorated method that stores its input and output history in Redis.
    """
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        """
        Wrapper function to store the input and output history in Redis.
        """
        # Store inputs
        input_key = f"{method.__qualname__}:inputs"
        output_key = f"{method.__qualname__}:outputs"
        
        self._redis.rpush(input_key, str(args))
        
        # Execute the original method and store the output
        output = method(self, *args, **kwargs)
        self._redis.rpush(output_key, str(output))
        
        return output
    
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
    @call_history
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


def replay(method: Callable):
    """
    Display the history of calls of a particular function.
    
    Args:
        method (Callable): The method for which the call history is to be displayed.
    """
    # Create input and output keys based on the method's qualified name
    input_key = f"{method.__qualname__}:inputs"
    output_key = f"{method.__qualname__}:outputs"

    # Retrieve inputs and outputs from Redis
    inputs = method.__self__._redis.lrange(input_key, 0, -1)
    outputs = method.__self__._redis.lrange(output_key, 0, -1)

    # Display the history of calls
    print(f"{method.__qualname__} was called {len(inputs)} times:")
    for input_data, output_data in zip(inputs, outputs):
        print(f"{method.__qualname__}(*{input_data.decode('utf-8')}) -> {output_data.decode('utf-8')}")

