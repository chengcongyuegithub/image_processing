from test1.task_queue.task_model import *
from redis import ConnectionPool
import redis
import random
import json
import time
import sys
Pool = ConnectionPool(host='127.0.0.1', port=6379, max_connections=100)
conn = redis.Redis(connection_pool=Pool)
# 1---5
#randomeventtype = int(random.randint(1, 5))
# 1---2
#randomeventtype = int(random.randint(1, 2))

#for i in range(0,1000):
#    conn.lpush('task_queue',json.dumps(eventmodel2dict(EventModel(EventType(int(random.randint(1, 5))),1,EntityType(int(random.randint(1, 2))),2,3,{'pink':2,'red':3}))))

'''
conn.zadd('album1:2',{'1':time.time()})
conn.zadd('album1:2',{'2':time.time()})
conn.zadd('album1:2',{'3':time.time()})
conn.zadd('album1:2',{'4':time.time()})
'''
'''
print(conn.zcard('album1:2'))   
'''

#conn.zadd('album1:2',time.localtime(),2)
#conn.zadd('album1:2',time.localtime(),3)
#conn.zadd('album1:2',time.localtime(),10)
#print(conn.smembers('useralbum:2'))

#conn.zrem('album:1:1','8')
for e in conn.zrange('album:1:2',0,sys.maxsize,desc=True,withscores=False,score_cast_func=float):
    print(e)
    conn.zrem('album:1:2',e)