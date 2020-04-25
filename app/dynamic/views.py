from flask import *
from flask_login import login_required, current_user
from . import dynamic
from app import db, conn
from app.models import Dynamic, Image, Comment, User, ImageType
from app.views import showdynamic, byte2int
from app import fdfs_client, fdfs_addr
from event.event_queue import fireEvent
from event.model import EventType, EventModel, EntityType


@dynamic.route("/<dynamicid>", methods={'get', 'post'})
@login_required
def detail(dynamicid):
    dynamic = Dynamic.query.filter_by(id=dynamicid).first()
    if dynamic==None:
        abort(404)
    dict = showdynamic(dynamic, True)
    return render_template('dynamicdetail.html', dynamic=dict)


@dynamic.route("/adddynamic", methods={'get', 'post'})
@login_required
def index():
    if request.method == 'POST':
        content = request.values.get('dynamiccontent').strip()
        imgid = request.values.get('imgid')
        compareimgid = request.values.get('compareimgid')
        dynamic = Dynamic(content, current_user.id)
        db.session.add(dynamic)
        db.session.flush()
        db.session.commit()
        if imgid == None:
            files = request.files.getlist('dynamicimg')
            for f in files:
                filename = f.filename
                if filename == None or filename == '': break
                f = f.read()
                suffix = filename[filename.find('.') + 1:]
                url = fdfs_addr + fdfs_client.uploadbyBuffer(f, suffix)
                name = url[url.rfind('/') + 1:]
                img = Image(name, url, ImageType.ORIGIN, -1, current_user.id, dynamic.id)
                db.session.add(img)
            db.session.commit()
            fireEvent(EventModel(EventType.DYNAMIC, current_user.id, EntityType.DYNAMIC, dynamic.id, current_user.id,
                                 {'detail': '/dynamic/' + str(dynamic.id)}))
        else:
            img = Image.query.filter_by(id=imgid).first()
            compareimg = Image.query.filter_by(id=compareimgid).first()
            img.dynamic_id = dynamic.id
            compareimg.dynamic_id = dynamic.id
            db.session.commit()
            fireEvent(EventModel(EventType.SHARE, current_user.id, EntityType.DYNAMIC, dynamic.id, current_user.id,
                                 {'detail': '/dynamic/' + str(dynamic.id)}))
        return redirect('/')
    else:
        imgid = request.args.get('imgid')
        if imgid == None:
            return render_template('adddynamic.html')
        else:
            content = ''
            img = Image.query.filter_by(id=imgid).first()  # 处理之后的图片
            if ImageType(img.action) == ImageType.SRCNN:
                compareimg = Image.query.filter_by(id=img.orig_id).first()  # 原图
                content = '原图和系统处理过之后的图片比较'
            elif ImageType(img.action) == ImageType.UPSCALE_2X:
                compareimg = Image.query.filter_by(orig_id=img.orig_id,
                                                   action=ImageType.BICUBIC_UPSCALE_2X.value).first()
                content = '传统的2x处理和系统SRCNN的2x处理的图片比较'
            elif ImageType(img.action) == ImageType.UPSCALE_3X:
                compareimg = Image.query.filter_by(orig_id=img.orig_id,
                                                   action=ImageType.BICUBIC_UPSCALE_3X.value).first()
                content = '传统的3x处理和系统SRCNN的3x处理的图片比较'
            return render_template('adddynamic.html', img=img, compareimg=compareimg, content=content)


@dynamic.route("/delete", methods={'get', 'post'})
def delete():
    data = json.loads(request.get_data(as_text=True))
    dynamicid = data['dynamicid']
    dynamic = Dynamic.query.filter_by(id=dynamicid).first()
    # 删除内容
    db.session.delete(dynamic)
    db.session.commit()
    # 处理图片
    imgs = Image.query.filter_by(dynamic_id=int(dynamicid)).all()
    for img in imgs:
        # 看当前图片是不是属于某个相册，如果属于的话，表明它是分享系统的动态，仅仅是改变属性
        rediskey = 'useralbum:' + str(current_user.id)
        flag = False
        for albumid in conn.smembers(rediskey):
            albumid = byte2int(albumid)
            rediskey2 = 'album:' + str(current_user.id) + ':' + str(albumid)
            isalbum = conn.zrank(rediskey2, img.id)
            if isinstance(isalbum, int):  # 是相册的
                img.dynamic_id = -1
                flag = True
                break
        if (flag == False):
            fdfs_client.delete(img.url[len(fdfs_addr):])
            db.session.delete(img)
    db.session.commit()
    # 处理评论
    comments = Comment.query.filter_by(entityType=EntityType.DYNAMIC.value, entityId=dynamicid).all()
    for comment in comments:
        deletecomments(comment.id,[])
    # 处理点赞
    rediskey = 'like:' + dynamicid
    likecount = conn.scard(rediskey)
    conn.delete(rediskey)
    rediskey2 = 'likeuser:' + str(current_user.id)
    conn.set(rediskey2, int(conn.get(rediskey2)) - likecount)
    return jsonify(code=200, message='删除成功')


@dynamic.route("/more", methods={'get', 'post'})
def more():
    data = json.loads(request.get_data(as_text=True))
    id = data['id']
    dynamic = Dynamic.query.filter_by(id=id).first()
    return jsonify(code=200, content=dynamic.content)


@dynamic.route("/packup", methods={'get', 'post'})
def packup():
    data = json.loads(request.get_data(as_text=True))
    id = data['id']
    dynamic = Dynamic.query.filter_by(id=id).first()
    return jsonify(code=200, content=dynamic.content[0:200])


@dynamic.route("/comment", methods={'get', 'post'})
def comment():
    if isinstance(current_user.is_anonymous, bool):
        return jsonify(code=400, message='用户尚未登录，无法评论')
    data = json.loads(request.get_data(as_text=True))
    type = data['type']
    id = data['id']
    content = data['content']
    userid = data['userid']
    if type == 'dynamic':
        comment = Comment(content, current_user.id, EntityType.DYNAMIC, id)
        dynamic=Dynamic.query.filter_by(id=int(id)).first()
        db.session.add(comment)
        db.session.flush()
        db.session.commit()
        if dynamic.user_id!=current_user.id:
            fireEvent(EventModel(EventType.COMMENT, current_user.id, EntityType.DYNAMIC, id, dynamic.user_id,
                             {'detail': '/dynamic/' + id,'name':current_user.nickname}))
        return jsonify(code=200, username=current_user.nickname, userid=current_user.id, content=content,
                       commentid=comment.id)
    else:
        if int(userid) == current_user.id:
            return jsonify(code=400, message='用户不能回复自己')
        actoruser = User.query.filter_by(id=userid).first()
        comment = Comment(content, current_user.id, EntityType.COMMENT, id)
        db.session.add(comment)
        db.session.commit()
        fireEvent(EventModel(EventType.COMMENT, current_user.id, EntityType.COMMENT, id, userid,
                             {'detail': '/dynamic/' + id, 'name': current_user.nickname}))
        return jsonify(code=201, username=current_user.nickname, userid=current_user.id, content=content,
                       commentid=comment.id, actorname=actoruser.nickname)


@dynamic.route("/deletecomment", methods={'get', 'post'})
def deletecomment():
    data = json.loads(request.get_data(as_text=True))
    commentid = data['commentid']
    #comment = Comment.query.filter_by(id=commentid).first()
    #db.session.delete(comment)
    #db.session.commit()
    commentlist=[]
    deletecomments(int(commentid),commentlist)
    return jsonify(code=200,commentlist=commentlist)

def deletecomments(commentid,commentlist):
    comment = Comment.query.filter_by(id=commentid).first()
    commentlist.append(comment.id)
    db.session.delete(comment)
    comments=Comment.query.filter_by(entityType=EntityType.COMMENT.value,entityId=comment.id).all()
    if len(comments)==0:
        db.session.commit()
        return
    for comment in comments:
        deletecomments(comment.id,commentlist)

@dynamic.route('/like', methods={'get', 'post'})
def like():
    data = json.loads(request.get_data(as_text=True))
    dynamicid = data['dynamicid']
    # 是否点赞过
    dynamic = Dynamic.query.filter_by(id=dynamicid).first()
    rediskey = 'like:' + dynamicid
    rediskey2 = 'likeuser:' + str(dynamic.user_id)
    if isinstance(current_user.is_anonymous, bool):
        return jsonify(code=400, message='用户尚未登录，无法点赞')
    if conn.sismember(rediskey, current_user.id):  # 如果已经点赞过
        conn.srem(rediskey, current_user.id)
        conn.set(rediskey2, int(conn.get(rediskey2)) - 1)
        return jsonify(code=201, likecount=conn.scard(rediskey))
    else:
        conn.sadd(rediskey, current_user.id)
        if conn.get(rediskey2) != None:
            conn.set(rediskey2, int(conn.get(rediskey2)) + 1)
        else:
            conn.set(rediskey2, 1)
        return jsonify(code=200, likecount=conn.scard(rediskey))
