from flask import *
from flask_login import login_required, current_user
from . import dynamic
from app import db, conn
from app.models import Dynamic, Image, Comment, User, ImageType
from app.views import getAllComment
from app import fdfs_client, fdfs_addr
from event.event_queue import fireEvent
from event.model import EventType, EventModel, EntityType


@dynamic.route("/<dynamicid>", methods={'get', 'post'})
@login_required
def detail(dynamicid):
    dynamic = Dynamic.query.filter_by(id=dynamicid).order_by(Dynamic.changetime.desc()).first()
    user = User.query.filter_by(id=dynamic.user_id).first()
    dict = {}
    dict['name'] = user.nickname
    dict['headurl'] = user.head_url
    dict['time'] = dynamic.changetime
    dict['content'] = dynamic.content
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
        db.session.add(comment)
        db.session.flush()
        db.session.commit()
        fireEvent(EventModel(EventType.COMMENT, current_user.id, EntityType.DYNAMIC, id, userid,
                             { 'detail': '/dynamic/' + id}))
        return jsonify(code=200, username=current_user.nickname, userid=current_user.id, content=content,
                       commentid=comment.id)
    else:
        if int(userid) == current_user.id:
            return jsonify(code=400, message='用户不能回复自己')
        actoruser = User.query.filter_by(id=userid).first()
        comment = Comment(content, current_user.id, EntityType.COMMENT, id)
        db.session.add(comment)
        db.session.commit()
        return jsonify(code=201, username=current_user.nickname, userid=current_user.id, content=content,
                       commentid=comment.id, actorname=actoruser.nickname)


@dynamic.route("/deletecomment", methods={'get', 'post'})
def deletecomment():
    data = json.loads(request.get_data(as_text=True))
    commentid = data['commentid']
    comment = Comment.query.filter_by(id=commentid).first()
    db.session.delete(comment)
    db.session.commit()
    return jsonify(code=200)


@dynamic.route('/like', methods={'get', 'post'})
def like():
    data = json.loads(request.get_data(as_text=True))
    dynamicid = data['dynamicid']
    # 是否点赞过
    img = Image.query.filter_by(dynamic_id=dynamicid).first()
    rediskey = 'like:' + dynamicid
    rediskey2 = 'likeuser:' + str(img.user_id)
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
