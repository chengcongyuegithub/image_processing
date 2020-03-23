from .task_model import *

class EventHandler():
    def dohandler(self, eventModel):
        raise NotImplementedError

    def getSupportEventTypes(self):
        raise NotImplementedError


class FollowEventHandler(EventHandler):
    def __init__(self):
        print('FollowEventHandler被创建了')

    def dohandler(self, eventModel):
        print('处理关注取消关注的事件')

    def getSupportEventTypes(self):
        return [EventType.FOLLOW, EventType.UNFOLLOW]


class LikeEventHandler(EventHandler):
    def __init__(self):
        print('LikeEventHandler被创建了')

    def dohandler(self, eventModel):
        print('处理点赞点踩的事件')

    def getSupportEventTypes(self):
        return [EventType.LIKE, EventType.UNLIKE]


class CommentEventHandler(EventHandler):
    def __init__(self):
        print('CommentEventHandler被创建了')

    def dohandler(self, eventModel):
        print('处理评论的事件')

    def getSupportEventTypes(self):
        return [EventType.COMMENT]


class QuestionEventHandler(EventHandler):
    def __init__(self):
        print('QuestionEventHandler被创建了')

    def dohandler(self, eventModel):
        print('处理提出问题的事件')

    def getSupportEventTypes(self):
        return [EventType.QUESTION]
