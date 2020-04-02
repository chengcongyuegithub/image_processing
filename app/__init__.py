from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from .configs import *
from flask_bootstrap import Bootstrap
from redis import ConnectionPool
from concurrent.futures import ThreadPoolExecutor
from flask_socketio import SocketIO, emit
import redis
from fastdfs.fastdfsUtil import Fdfs
import os
import tensorflow as tf
import cv2 as cv

# 绑定数据库操作
# 操作flask的对象
app = Flask(__name__)
# 加载配置
app.config.from_object(configs)
# db绑定app
db = SQLAlchemy(app)
app.secret_key = 'image_processing'
# 绑定bootstrap
bootstrap = Bootstrap(app)
# redis的连接
Pool = ConnectionPool(host='127.0.0.1', port=6379, max_connections=100)
conn = redis.Redis(connection_pool=Pool)
# fastdfs图片服务器
fastdfs_client = os.path.join(os.getcwd(), "fastdfs", 'client.conf')
fdfs_client = Fdfs(fastdfs_client)
fdfs_addr = 'http://192.168.158.20:88/'
# 处理大型任务的线程池
largetaskexecutor = ThreadPoolExecutor(max_workers=4)
# websocket服务器
socketio = SocketIO(app)

from event.handler import EventHandler
# handler初始化
handlerdict={}
for sc in EventHandler.__subclasses__():
    handler=sc()
    for eventType in handler.getSupportEventTypes():
        if handlerdict.__contains__(eventType.name):
            handlerdict[eventType.name].append(handler)
        else:
            handlerdict[eventType.name]=[]
            handlerdict[eventType.name].append(handler)
# 异步任务消费者线程启动
from event.event_queue import *
EventThread('task_queue_thread').start()

from .models import *

# 用户模块
from .user import user as user_blueprint
app.register_blueprint(user_blueprint, url_prefix='/user')

# 图片模块
from .image import image as image_blueprint
app.register_blueprint(image_blueprint, url_prefix='/image')

# 相册模块
from .album import album as album_blueprint
app.register_blueprint(album_blueprint, url_prefix='/album')

# 相册模块
from .dynamic import dynamic as dynamic_blueprint
app.register_blueprint(dynamic_blueprint, url_prefix='/dynamic')

# 主页
from . import views