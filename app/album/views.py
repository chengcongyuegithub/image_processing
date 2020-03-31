from flask import *
from flask_login import login_required, current_user
from . import album
from app.models import Photoalbum, Image,ImageType
from app import fdfs_client, fdfs_addr, db, conn
from app.views import byte2int
from event.event_queue import fireEvent
from event.model import EventType, EventModel, EntityType
import sys


@album.route("/<albumid>")
@login_required
def index(albumid):
    rediskey = 'album:' + str(current_user.id) + ':' + albumid
    imglist = []
    for imgid in conn.zrange(rediskey, 0, sys.maxsize, desc=True, withscores=False, score_cast_func=float):
        #imgid = str(imgid, encoding="utf-8")
        #imgid = int(imgid)
        imgid=byte2int(imgid)
        img = Image.query.filter_by(id=imgid).first()
        imglist.append(img)
    return render_template('albumdetail.html', imglist=imglist, albumid=albumid)


@album.route("/ajaxdetail", methods={'get', 'post'})
@login_required
def ajaxdetail():
    data = json.loads(request.get_data(as_text=True))
    albumid = data['albumid']
    rediskey = 'album:' + str(current_user.id) + ':' + albumid
    imglist = []
    for imgid in conn.zrange(rediskey, 0,sys.maxsize, desc=True, withscores=False, score_cast_func=float):
        dict={}
        imgid = byte2int(imgid)
        img = Image.query.filter_by(id=imgid).first()
        if ImageType(img.action)==ImageType.ORIGIN:
            proimg = Image.query.filter_by(orig_id=imgid).first()
            if proimg!=None: continue;
            dict['url']=img.url
            dict['id']=img.id
            imglist.append(dict)
        if len(imglist)==6: break
    return jsonify(code=200, imglist=imglist, albumid=albumid)


@album.route("/updatealbum", methods={'get', 'post'})
@login_required
def update():
    albumid = request.values.get('albumid').strip()
    photoalbum = Photoalbum.query.filter_by(id=int(albumid)).first()
    return render_template('updatealbum.html', photoalbum=photoalbum)


@album.route("/updatealb", methods={'get', 'post'})
@login_required
def updatealb():
    if request.method == 'POST':
        albumid = request.values.get('albumid').strip()
        if int(albumid) == 1:
            return redirect('/user/useralbum')
        name = request.values.get('name').strip()
        introduce = request.values.get('introduce').strip()
        f = request.files['updatefrontcover']
        album = Photoalbum.query.filter_by(id=albumid).first()
        orginlname = album.name
        album.name = name
        album.introduce = introduce
        if f.filename != '':
            filename = f.filename
            f = f.read()
            suffix = filename[filename.find('.') + 1:]
            url = fdfs_addr + fdfs_client.uploadbyBuffer(f, suffix)
            album.front_cover = url
        db.session.commit()
        fireEvent(EventModel(EventType.ALBUM, -1, EntityType.USER, album.id, current_user.id,
                             {'orginlname': orginlname, 'action': '修改'}))

    return redirect('/user/useralbum')


@album.route("/addalbum", methods={'get', 'post'})
@login_required
def add():
    return render_template('addalbum.html')


@album.route("/addalb", methods={'get', 'post'})
@login_required
def addalb():
    if request.method == 'POST':
        name = request.values.get('name').strip()
        introduce = request.values.get('introduce').strip()
        f = request.files['addfrontcover']
        filename = f.filename
        if filename != '':
            f = f.read()
            suffix = filename[filename.find('.') + 1:]
            url = fdfs_addr + fdfs_client.uploadbyBuffer(f, suffix)
        else:
            url = '/static/img/kittens.jpg'
        # 数据库添加字典的内容
        photoalbum = Photoalbum(name, introduce, url)
        db.session.add(photoalbum)
        db.session.flush()
        db.session.commit()
        # 当前用户添加字典的id
        rediskey = 'useralbum:' + str(current_user.id)
        conn.sadd(rediskey, photoalbum.id)
        # 给用户发私信
        fireEvent(EventModel(EventType.ALBUM, -1, EntityType.USER, photoalbum.id, current_user.id,
                             {'orginlname': name, 'action': '新建'}))
    return redirect('/user/useralbum')


@album.route("/delete", methods={'get', 'post'})
@login_required
def delete():
    data = json.loads(request.get_data(as_text=True))
    albumid = data['albumid']
    name = Photoalbum.query.filter_by(id=albumid).first().name
    # 删除封面
    rediskey = 'useralbum:' + str(current_user.id)
    conn.srem(rediskey, albumid)
    # 删除内容----异步
    fireEvent(EventModel(EventType.TASK, current_user.id, EntityType.ALBUM, albumid, current_user.id,
                         {'task': 'deleteinbatch', 'orginlname': name, 'action': '删除'}))
    return jsonify(code=200)
