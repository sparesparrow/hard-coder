### Response Cache Pattern
**Intent**: Optimize response time and resource usage through intelligent caching.

**Solution**:  
```python
class ResponseCache:
    def __init__(self, ttl=3600):  
        self.cache = {}
        self.ttl = ttl

    def get_response(self, query_hash):
        if self.cache.has(query_hash):
            cached = self.cache.get(query_hash)
            if self.is_valid(cached):
                return cached.response

        return None  

    def store_response(self, query_hash, response):
        self.cache[query_hash] = {
            'response': response, 
            'timestamp': time.time()
        }
```
