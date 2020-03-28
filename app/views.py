from flask import *
from app import app, db
from .models import Dynamic, Image, User, Comment


@app.route("/")
def index():
    # 动态
    dynamiclist = Dynamic.query.order_by(Dynamic.changetime.desc()).all()
    indexlist = []
    for dynamic in dynamiclist:
        dict = {}
        dict['time'] = dynamic.changetime
        dict['content'] = dynamic.content
        dict['id'] = dynamic.id
        imgs = Image.query.filter_by(dynamic_id=dynamic.id).all()
        imglist = []
        for img in imgs:
            imglist.append(img.url)
            if dict.__contains__('name') == False:
                user = User.query.filter_by(id=img.user_id).first()
                dict['name'] = user.nickname
                dict['headurl'] = user.head_url
        dict['imgs'] = imglist
        commentslist=[]
        getAllComment(commentslist,dynamic.id)
        dict['comments']=commentslist
        indexlist.append(dict)
    return render_template('index.html', indexlist=indexlist)

def getAllComment(commentslist,id):
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
        f(comment.id, commentslist,user.nickname)

def f(id,list,parentname):
    comments = Comment.query.filter_by(entityType=3, entityId=id).all()
    if comments==None: return
    for comment in comments:
        commentdict = {}
        user = User.query.filter_by(id=comment.entityOwnerId).first()
        commentdict['id'] = comment.id
        commentdict['userid'] = user.id
        commentdict['name'] = user.nickname
        commentdict['actorname'] = parentname
        commentdict['content'] = comment.content
        list.append(commentdict)
        f(comment.id,list,user.nickname)