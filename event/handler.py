from .model import EventType
from app.models import Message
from app import db,largetaskexecutor
from .largetask import deleteinbatch,srcnn_process
taskflag=True
taskstr='???????'

class EventHandler():
    def dohandler(self, eventModel):
        raise NotImplementedError

    def getSupportEventTypes(self):
        raise NotImplementedError


class FollowEventHandler(EventHandler):
    def __init__(self):
        print('FollowEventHandler被创建了')

    def dohandler(self, eventModel):
        print('关注事件发生的时候')

    def getSupportEventTypes(self):
        return [EventType.FOLLOW, EventType.UNFOLLOW]


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
        print('评论事件发生的时候')

    def getSupportEventTypes(self):
        return [EventType.COMMENT]


class RegistEventHandler(EventHandler):
    def __init__(self):
        print('RegistEventHandler被创建了')

    def dohandler(self, eventModel):
        message = Message(-1, eventModel.entityId, '欢迎来到图片处理系统!!!')
        db.session.add(message)
        db.session.commit()

    def getSupportEventTypes(self):
        return [EventType.REGIST]


class FeedEventHandler(EventHandler):
    def __init__(self):
        print('RegistEventHandler被创建了')

    def dohandler(self, eventModel):
        print('注册成功的时候')

    def getSupportEventTypes(self):
        return [EventType.COMMENT, EventType.DYNAMIC]


class AlbumEventHandler(EventHandler):
    def __init__(self):
        print('AlbumEventHandler被创建了')

    def dohandler(self, eventModel):
        message = Message(-1, eventModel.entityOwnerId,
                          '您刚刚' + eventModel.dict['action'] + '了名称为 ' + eventModel.dict['orginlname'] + ' 的相册信息')
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
            if task.result():
                message = Message(-1, eventModel.entityOwnerId,
                                  '您刚刚' + eventModel.dict['action'] + '了名称为 ' + eventModel.dict[
                                      'orginlname'] + ' 的相册信息和内容')
                db.session.add(message)
                db.session.commit()
        elif eventModel.dict['task'] == 'srcnn_process':
            task = largetaskexecutor.submit(srcnn_process,eventModel.entityId,eventModel.dict['albumid'],eventModel.entityOwnerId)
            if task.result():
                message = Message(-1, eventModel.entityOwnerId,
                                  '图片优化已经完成，请访问图片所在的相册')
                db.session.add(message)
                db.session.commit()

    def getSupportEventTypes(self):
        return [EventType.TASK]
