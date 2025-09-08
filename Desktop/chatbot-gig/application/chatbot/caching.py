import redis

redisClient = redis.Redis(host='localhost', port=6379, decode_responses=True)


REDIS_TTL = 3600  # keep history for 1 hour
