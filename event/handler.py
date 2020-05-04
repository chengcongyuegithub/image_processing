from .model import EventType, EntityType
from app.models import Message, MessageType, User, Feed, ImageType
from app import db, largetaskexecutor, conn, socketio, emit
from .largetask import deleteinbatch, srcnn_process
import sys
import time
import json

class EventHandler():
    def dohandler(self, eventModel):
        raise NotImplementedError

    def getSupportEventTypes(self):
        raise NotImplementedError


class FollowEventHandler(EventHandler):
    def __init__(self):
        print('FollowEventHandler被创建了')

    def dohandler(self, eventModel):
        userid = eventModel.entityId
        message = Message(eventModel.actorId, userid, '名为 ' + eventModel.dict['name'] + ' 的用户关注了你',
                          MessageType.NOTICE, '')
        db.session.add(message)
        db.session.commit()

    def getSupportEventTypes(self):
        return [EventType.FOLLOW]


class UnFollowEventHandler(EventHandler):
    def __init__(self):
        print('UnFollowEventHandler')

    def dohandler(self, eventModel):
        # print('取消关注的事件发生了')
        # 得到取消关注人的id，获取它的新鲜事列表，获取当前操作用户的新鲜事流，按照顺序删除
        userid = eventModel.entityId
        db.session.commit()
        feedlist = Feed.query.filter_by(userId=userid).order_by(Feed.createtime.desc()).all()
        count=0
        feedline = 'feedline:' + str(eventModel.actorId)
        for feedid in conn.zrange(feedline, 0, sys.maxsize, desc=True, withscores=False, score_cast_func=float):
            feedid = str(feedid, encoding="utf-8")
            feedid = int(feedid)
            if count<=len(feedlist)-1 and feedid==feedlist[count].id:
                conn.zrem(feedline, feedid)
                count=count+1

    def getSupportEventTypes(self):
        return [EventType.UNFOLLOW]


class LikeEventHandler(EventHandler):
    def __init__(self):
        print('LikeEventHandler被创建了')

    def dohandler(self, eventModel):
        print('点赞事件发生的时候')

    def getSupportEventTypes(self):
        return [EventType.LIKE, EventType.UNLIKE]


class CommentEventHandler(EventHandler):
    def __init__(self):
        print('CommentEventHandler被创建了')

    def dohandler(self, eventModel):
        if eventModel.entityType == EntityType.DYNAMIC:
            message = Message(eventModel.actorId, eventModel.entityOwnerId,
                              '名为 ' + eventModel.dict['name'] + ' 的人评论了你的动态',
                              MessageType.NOTICE, eventModel.dict['detail'])
        else:
            message = Message(eventModel.actorId, eventModel.entityOwnerId,
                              '名为 ' + eventModel.dict['name'] + ' 的人回复了你的评论',
                              MessageType.NOTICE, eventModel.dict['detail'])
        db.session.add(message)
        db.session.commit()

    def getSupportEventTypes(self):
        return [EventType.COMMENT]


class RegistEventHandler(EventHandler):
    def __init__(self):
        print('RegistEventHandler被创建了')

    def dohandler(self, eventModel):
        print(type(MessageType.NOTICE.value))
        message = Message(-1, eventModel.entityId, '欢迎来到图片处理系统!!!', MessageType.NOTICE, '')
        db.session.add(message)
        db.session.commit()

    def getSupportEventTypes(self):
        return [EventType.REGIST]


class FeedEventHandler(EventHandler):
    def __init__(self):
        print('FeedEventHandler被创建了')

    def dohandler(self, eventModel):
        # 评论评论不算做新鲜事
        if eventModel.entityType == EntityType.COMMENT:
            return
        followerkey = 'follower:1:' + str(eventModel.actorId)
        feed = Feed(eventModel.eventType, eventModel.actorId, json.dumps(eventModel.dict))
        db.session.add(feed)
        db.session.flush()
        db.session.commit()
        for userid in conn.zrange(followerkey, 0, sys.maxsize, desc=True, withscores=False, score_cast_func=float):
            userid = str(userid, encoding="utf-8")
            userid = int(userid)
            user = User.query.filter_by(id=userid).first()
            feedline = 'feedline:' + str(user.id)
            conn.zadd(feedline, {feed.id: time.time()})

    def getSupportEventTypes(self):
        return [EventType.COMMENT, EventType.DYNAMIC, EventType.FOLLOW, EventType.SHARE]


class AlbumEventHandler(EventHandler):
    def __init__(self):
        print('AlbumEventHandler被创建了')

    def dohandler(self, eventModel):
        message = Message(-1, eventModel.entityOwnerId,
                          '您刚刚' + eventModel.dict['action'] + '了名称为 ' + eventModel.dict['orginlname'] + ' 的相册信息',
                          MessageType.NOTICE, '')
        db.session.add(message)
        db.session.commit()

    def getSupportEventTypes(self):
        return [EventType.ALBUM]


class TaskEventHandler(EventHandler):
    def __init__(self):
        print('TaskEventHandler被创建了')

    def dohandler(self, eventModel):
        if eventModel.dict['task'] == 'deleteinbatch':
            task = largetaskexecutor.submit(deleteinbatch, eventModel.actorId, eventModel.entityId)
            #if task.result():
                # message = Message(-1, eventModel.entityOwnerId,'您刚刚' + eventModel.dict['action'] + '了名称为 ' + eventModel.dict['orginlname'] + ' 的相册信息和内容',MessageType.NOTICE)
                # db.session.add(message)
                # db.session.commit()
                # socketio.emit('noreadmsg', {'data': '20'})
                #print('!!!!')
        elif eventModel.dict['task'] == 'srcnn_process':
            if ImageType(eventModel.dict['action']) == ImageType.SRCNN:  # 清晰化处理
                print('清晰化处理')
                task = largetaskexecutor.submit(srcnn_process, eventModel.entityId, eventModel.dict['albumid'],
                                                eventModel.entityOwnerId, eventModel.dict['action'])
            else:  # 放大处理
                print('放大处理')
                task = largetaskexecutor.submit(srcnn_process, eventModel.entityId, eventModel.dict['albumid'],
                                                eventModel.entityOwnerId, eventModel.dict['action'],
                                                eventModel.dict['time'])
            #if task.result():
                # message = Message(-1, eventModel.entityOwnerId,'图片放大已经完成，请访问图片所在的相册',MessageType.NOTICE)
                # db.session.add(message)
                # db.session.commit()
                #print('!!!!')

    def getSupportEventTypes(self):
        return [EventType.TASK]
