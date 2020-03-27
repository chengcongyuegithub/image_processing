from enum import Enum


class EventType(Enum):
    COMMENT = 1
    FOLLOW = 2
    UNFOLLOW = 3
    LIKE = 4
    UNLIKE = 5
    DYNAMIC = 6
    REGIST = 7
    ALBUM = 8
    TASK = 9 #大任务量

class EntityType(Enum):
    USER = 1
    DYNAMIC = 2
    COMMENT = 3
    ALBUM = 4
    IMAGE = 5


class EventModel(object):
    def __init__(self, eventType, actorId, entityType, entityId, entityOwnerId, dict):
        self.eventType = eventType
        self.actorId = actorId
        self.entityType = entityType
        self.entityId = entityId
        self.entityOwnerId = entityOwnerId
        self.dict = dict

    def __repr__(self):
        return '<EventModel %s %s %s %s %s>' % (
            self.eventType.name, self.actorId, self.entityType.name, self.entityOwnerId, self.dict)


def eventmodel2dict(eventmodel):
    return {
        'eventType': eventmodel.eventType.value,
        'actorId': eventmodel.actorId,
        'entityType': eventmodel.entityType.value,
        'entityId': eventmodel.entityId,
        'entityOwnerId': eventmodel.entityOwnerId,
        'dict': eventmodel.dict
    }


def dict2eventmodel(dict):
    return EventModel(EventType(int(dict['eventType'])), int(dict['actorId']), EntityType(int(dict['entityType'])),
                      int(dict['entityId']),
                      int(dict['entityOwnerId']), dict['dict'])
