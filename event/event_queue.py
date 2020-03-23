import threading
import json
from .model import dict2eventmodel,eventmodel2dict
from app import conn,handlerdict
class EventThread(threading.Thread):
    def __init__(self, threadName):
        threading.Thread.__init__(self)
        self.name = threadName

    def run(self):
        while(True):
            str1 = str(conn.brpop('task_queue')[1], encoding="utf-8")
            dict = eval(str1)
            eventmodel = dict2eventmodel(dict)
            for handler in handlerdict[eventmodel.eventType.name]:
                handler.dohandler(eventmodel)

def fireEvent(eventModel):
    conn.lpush('task_queue',json.dumps(eventmodel2dict(eventModel)))