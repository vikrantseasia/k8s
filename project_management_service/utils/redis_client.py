import redis

redis_client = redis.StrictRedis(
    host='localhost',  # Change to your Redis server host
    port=6379,         # Change to your Redis server port if different
    db=0,              # Use the appropriate Redis DB index
    decode_responses=True  # This ensures the responses are decoded to UTF-8
)