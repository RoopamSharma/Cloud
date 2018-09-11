import redis

r = redis.Redis(
    host='redis-14510.c8.us-east-1-4.ec2.cloud.redislabs.com',
    port=14510, 
    password='s3Z4e026H6WXhsPFXULl1pPsltR0hNyf')

r.set('foo', 'bar')
value = r.get('foo')
print(value)	