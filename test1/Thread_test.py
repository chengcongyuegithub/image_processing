from test1.task_queue.task_model import *
import threading
from redis import ConnectionPool
import redis
Pool=ConnectionPool(host='127.0.0.1',port=6379,max_connections=100)
conn = redis.Redis(connection_pool=Pool)

class MutliThread(threading.Thread):
    def __init__(self, threadName):
        threading.Thread.__init__(self)
        self.name = threadName

    def run(self):
        while(True):
            str1 = str(conn.brpop('task_queue')[1], encoding="utf-8")
            dict = eval(str1)
            eventmodel=dict2eventmodel(dict)
            print(eventmodel.eventType.name)

if __name__ == '__main__':
    thr1 = MutliThread('task_queue_thread')
    thr1.start()

