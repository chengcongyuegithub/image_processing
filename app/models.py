from app import db
import time
import random


class Dynamic(db.Model):
    __tablename__ = 'dynamic'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    content = db.Column(db.Text)
    changetime = db.Column(db.String(20))

    def __init__(self, content):
        self.content = content
        self.changetime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

    def __repr__(self):
        return '<Dynamic %s>' % (self.content)


class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(100))
    nickname = db.Column(db.String(100))
    password = db.Column(db.String(100))
    salt = db.Column(db.String(32))
    head_url = db.Column(db.String(100))
    changetime = db.Column(db.String(20))
    # 个性签名
    signature = db.Column(db.String(100))

    def __init__(self, username, password, salt=''):
        self.username = username
        self.nickname = username
        self.password = password
        self.head_url = self.head_url = 'http://images.nowcoder.com/head/' + str(random.randint(0, 1000)) + 't.png'
        self.salt = salt
        self.changetime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

    def __repr__(self):
        return '<User %s %s %s>' % (self.username, self.password, self.head_url)

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id


class Image(db.Model):
    __tablename__ = 'image'
    # 图片的id
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    # 图片的名称
    name = db.Column(db.String(100))
    # 地址
    url = db.Column(db.String(100))
    # 上传或者重建的时间
    changetime = db.Column(db.String(20))
    # 行为:Bicubic,SRCNN,Origin,Upscale_X
    # Bicubic:模糊处理,双三次插值
    # SRCNN:卷积神经网络处理
    # Origin:原图或者没有处理
    # Upscale_X:放大多少倍数,如Upscale_3X表示放大3倍
    action = db.Column(db.String(20))
    # 原图id
    # 如果是原图的话,表示为-1
    orig_id = db.Column(db.Integer)
    # 属于哪个用户
    user_id = db.Column(db.Integer)
    # 属于哪个动态
    dynamic_id = db.Column(db.Integer)

    def __init__(self, name, url, action, orig_id, user_id, dynamic_id):
        self.name = name
        self.url = url
        self.changetime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        self.action = action
        self.orig_id = orig_id
        self.user_id = user_id
        self.dynamic_id = dynamic_id

    def __repr__(self):
        return '<Image %s %s %s %s>' % (self.name, self.url, self.changetime, self.action)


class Photoalbum(db.Model):
    __tablename__ = 'Photoalbum'
    # id
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    # 相册的名称
    name = db.Column(db.String(100))
    # 相册的介绍
    introduce = db.Column(db.String(100))
    # 相册的封面
    front_cover = db.Column(db.String(100))

    def __init__(self, name, introduce, front_conver):
        self.name = name
        self.introduce = introduce
        self.front_cover = front_conver

    def __repr__(self):
        return '<Photoalbum %s %s %s>' % (self.name, self.introduce, self.front_cover)


class Comment(db.Model):
    __tablename__ = 'comment'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    content = db.Column(db.Text)
    entityOwnerId = db.Column(db.Integer)
    # 处理对象的类型
    entityType = db.Column(db.Integer)
    entityId = db.Column(db.Integer)
    changetime = db.Column(db.String(20))

    def __init__(self, content, entityOwnerId, entityType, entityId):
        self.content = content
        self.entityOwnerId = entityOwnerId
        self.entityType = entityType
        self.entityId = entityId
        self.changetime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

    def __repr__(self):
        return '<Comment %s %d %d %s>' % (self.name, self.entityType, self.entityId)


class Message(db.Model):
    __tablename__ = 'message'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    # 谁发来的
    fromId = db.Column(db.Integer)
    # 发给谁的
    toId = db.Column(db.Integer)
    content = db.Column(db.Text)
    createtime = db.Column(db.String(20))
    # 是否已读
    # 0未读
    # 1已读
    hasRead = db.Column(db.Integer)
    # fromid2toid的形式
    # fromid和toid中比较小的放在面前
    # fromid为10，toid为2
    # conversationId 2to10
    conversationId = db.Column(db.String(20))
    #action的类型，是谈话，还是通知
    action=db.Column(db.String(20))

    def __init__(self, fromId, toId, content):
        self.content = content
        self.fromId = fromId
        self.toId = toId
        self.createtime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        self.hasRead = 0  # 默认为未读
        if fromId == -1:
            self.conversationId = '-1'
        elif fromId < toId:
            self.conversationId = str(fromId) + 'to' + str(toId)
        else:
            self.conversationId = str(toId) + 'to' + str(fromId)

    def __repr__(self):
        return '<Message %d %d %s>' % (self.fromId, self.toId, self.content)
