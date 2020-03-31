from flask import *
from app import app, db, conn
from .models import Dynamic, Image, User, Comment
from flask_login import current_user


@app.route("/")
def index():
    # 动态
    dynamiclist = Dynamic.query.order_by(Dynamic.changetime.desc()).all()
    indexlist = []
    for dynamic in dynamiclist:
        user = User.query.filter_by(id=dynamic.user_id).first()
        dict = {}
        dict['name'] = user.nickname
        dict['headurl'] = user.head_url
        dict['time'] = dynamic.changetime
        if len(dynamic.content) > 200:
            dict['flag'] = True
        else:
            dict['flag'] = False
        dict['content'] = dynamic.content[0:200]
        dict['id'] = dynamic.id
        imgs = Image.query.filter_by(dynamic_id=dynamic.id).all()
        imglist = []
        for img in imgs:
            imglist.append(img.url)
        dict['imgs'] = imglist
        commentslist = []
        getAllComment(commentslist, dynamic.id)
        dict['comments'] = commentslist
        rediskey = 'like:' + str(dynamic.id)
        dict['likecount'] = conn.scard(rediskey)
        if isinstance(current_user.is_anonymous, bool):
            dict['likeflag'] = False
        else:
            dict['likeflag'] = conn.sismember(rediskey, current_user.id)
        indexlist.append(dict)
    return render_template('index.html', indexlist=indexlist)


def getAllComment(commentslist, id):
    comments = Comment.query.filter_by(entityType=2, entityId=id).all()
    for comment in comments:
        commentdict = {}
        user = User.query.filter_by(id=comment.entityOwnerId).first()
        commentdict['id'] = comment.id
        commentdict['userid'] = user.id
        commentdict['name'] = user.nickname
        commentdict['actorname'] = '-1'
        commentdict['content'] = comment.content
        commentslist.append(commentdict)
        f(comment.id, commentslist, user.nickname)


def f(id, list, parentname):
    comments = Comment.query.filter_by(entityType=3, entityId=id).all()
    if comments == None: return
    for comment in comments:
        commentdict = {}
        user = User.query.filter_by(id=comment.entityOwnerId).first()
        commentdict['id'] = comment.id
        commentdict['userid'] = user.id
        commentdict['name'] = user.nickname
        commentdict['actorname'] = parentname
        commentdict['content'] = comment.content
        list.append(commentdict)
        f(comment.id, list, user.nickname)


@app.route("/alert", methods=['post', 'get'])
def alert():
    alertcontent = request.values.get('alertmsg')
    return render_template('alert.html', alertcontent=alertcontent)


def byte2int(id):
    id = str(id, encoding="utf-8")
    id = int(id)
    return id
