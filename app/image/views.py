from . import image
from flask import *
from app import fdfs_client, fdfs_addr, db, conn, cv, tf
from app.models import Image,ImageType,Photoalbum
from app.views import byte2int
from flask_login import current_user
import time
import numpy as np
from PIL import Image as Img
from srcnn.model import SRCNN
from io import BytesIO
from event.event_queue import fireEvent
from event.model import EntityType, EventModel, EventType


@image.route("/uploader", methods={'get', 'post'})
def index():
    if request.method == 'POST':
        f = request.files['txt_file']
        albumid = request.values.get('albumid')
        filename = f.filename
        f = f.read()
        suffix = filename[filename.find('.') + 1:]
        url = fdfs_addr + fdfs_client.uploadbyBuffer(f, suffix)
        name = url[url.rfind('/') + 1:]
        # 上传到数据库
        img = Image(name, url, ImageType.ORIGIN, -1, current_user.id, -1)
        db.session.add(img)
        db.session.flush()
        db.session.commit()
        # 添加到相册中，默认是添加到系统相册中
        if albumid == None or albumid == '' or albumid == '1':
            rediskey = 'album:' + str(current_user.id) + ':1'
        else:# 指定相册
            rediskey = 'album:' + str(current_user.id) + ':' + albumid
        conn.zadd(rediskey, {img.id: time.time()})
        return jsonify(code=200, message="success upload")
    else:
        return render_template('uploader.html')


@image.route("/detail", methods={'get', 'post'})
def detail():
    imgid = request.values.get('imgid').strip()
    img = Image.query.filter_by(id=imgid).first()
    return render_template('imagedetail.html', img=img)


@image.route("/delete", methods={'get', 'post'})
def delete():
    data = json.loads(request.get_data(as_text=True))
    imgid = data['imgid']
    albumid = data['albumid']
    img = Image.query.filter_by(id=imgid).first()
    if img.dynamic_id!=-1:
        return jsonify(code=400,message='该图片发布到动态中，如果想删除，请先删除动态')
    imgs = Image.query.filter_by(orig_id=imgid).all()
    if len(imgs):
        for im in imgs:
            fdfs_client.delete(im.url[len(fdfs_addr):])
            db.session.delete(im)
            db.session.commit()
            # 删除redis
            rediskey = 'album:' + str(current_user.id) + ':' + albumid
            conn.zrem(rediskey, im.id)
    # 删除mysql
    fdfs_client.delete(img.url[len(fdfs_addr):])
    db.session.delete(img)
    db.session.commit()
    # 删除redis
    rediskey = 'album:' + str(current_user.id) + ':' + albumid
    conn.zrem(rediskey, imgid)
    if len(imgs):
        return jsonify(code=201)
    return jsonify(code=200)


@image.route('/upscaling', methods=['GET', 'POST'])
def upscaling():
    data = json.loads(request.get_data(as_text=True))
    imgid = data['imgid']
    albumid = data['albumid']
    time = data['time']
    upscalingimg = Image.query.filter_by(id=imgid).first()
    # 对于已经处理过的情况的处理
    if ImageType(upscalingimg.action) != ImageType.ORIGIN:
        return jsonify(code=400, message='此图片为处理过的图片，请选择其他功能')
    if time=='2x':
        upscalingimg = Image.query.filter_by(action=ImageType.UPSCALE_2X.value, orig_id=imgid).first()
    else:
        upscalingimg = Image.query.filter_by(action=ImageType.UPSCALE_3X.value, orig_id=imgid).first()
    if upscalingimg != None:
        return jsonify(code=400, message='此图片已经优化过,请在该相册中查找')
    img = Image.query.filter_by(id=imgid).first()
    suffix = img.name[img.name.find('.') + 1:]
    imgContent = fdfs_client.downloadbyBuffer(img.url[len(fdfs_addr):])
    img = cv.imdecode(np.frombuffer(imgContent, np.uint8), cv.IMREAD_COLOR)
    print(img.shape)
    if time=='3x' and (img.shape[0] > 500 or img.shape[1] > 500):
        return jsonify(code=400, message='该图片尺寸较大，将无法执行放大操作，请选择其他操作')
    if time=='2x' and (img.shape[0] > 800 or img.shape[1] > 800):
        return jsonify(code=400, message='该图片尺寸较大，将无法执行放大操作，请选择其他操作')
    # 丢给线程池
    if time == '3x':
        fireEvent(EventModel(EventType.TASK, current_user.id, EntityType.IMAGE, imgid, current_user.id,
                         {'task': 'srcnn_process', 'action': ImageType.UPSCALE_3X.value, 'suffix': suffix, 'albumid': albumid,
                          'time': time}))
    elif time=='2x':
        fireEvent(EventModel(EventType.TASK, current_user.id, EntityType.IMAGE, imgid, current_user.id,
                             {'task': 'srcnn_process', 'action': ImageType.UPSCALE_2X.value, 'suffix': suffix,
                              'albumid': albumid,
                              'time': time}))
    return jsonify(code=200, message='得到的图片较大，稍后请刷新相册页面')


@image.route('/superresolution', methods=['GET', 'POST'])
def superresolution():
    if request.method == 'POST':
        data = json.loads(request.get_data(as_text=True))
        imgid = data['imgid']
        albumid = data['albumid']
        flag = data['flag']
        srcnnimg = Image.query.filter_by(id=imgid).first()
        if ImageType(srcnnimg.action)!=ImageType.ORIGIN:
            return jsonify(code=400, message='此图片为处理过的图片，请选择其他功能')
        srcnnimg = Image.query.filter_by(action=ImageType.SRCNN.value, orig_id=imgid).first()
        if srcnnimg != None:
            return jsonify(code=400, message='此图片已经优化过,请在该相册中查找')
        img = Image.query.filter_by(id=imgid).first()
        suffix = img.name[img.name.find('.') + 1:]
        imgContent = fdfs_client.downloadbyBuffer(img.url[len(fdfs_addr):])
        img = cv.imdecode(np.frombuffer(imgContent, np.uint8), cv.IMREAD_COLOR)
        if img.shape[0] > 1500 or img.shape[1] > 1500:
            return jsonify(code=400, message='该图片尺寸较大,执行该操作会导致内存泄漏')
        if img.shape[0] > 900 or img.shape[1] > 900:  # 大型任务，交给线程池处理
            fireEvent(EventModel(EventType.TASK, current_user.id, EntityType.IMAGE, imgid, current_user.id,
                                 {'task': 'srcnn_process', 'action': ImageType.SRCNN.value, 'suffix': suffix,
                                  'albumid': albumid}))
            if flag==True:
                return jsonify(code=203, message='请去图片所在相册查看结果')
            return jsonify(code=201, message='得到的图片较大，稍后请刷新相册页面')
        else:  # 小图片直接处理
            with tf.Session() as sess:
                srcnn = SRCNN(sess, "\srcnn\checkpoint\srcnn_21")
                img = srcnn.superresolution(img)
            img = Img.fromarray(img)
            f = BytesIO()
            img.save(f, format='PNG')
            f = f.getvalue()
            # 保存并上传数据库
            url = fdfs_addr + fdfs_client.uploadbyBuffer(f, suffix)
            imgname = url[url.rfind('/') + 1:]
            newimg = Image(imgname, url, ImageType.SRCNN, imgid, current_user.id, -1)
            db.session.add(newimg)
            db.session.flush()
            db.session.commit()
            if albumid == None or albumid == '' or albumid == '1':
                rediskey = 'album:' + str(current_user.id) + ':1'
            else:
                rediskey = 'album:' + str(current_user.id) + ':' + albumid
            conn.zadd(rediskey, {newimg.id: time.time()})
            # 系统统计
            for i in range(0,2):
                dictstr=conn.rpop('count')
                dict=eval(dictstr)
                dict['count']=int(dict['count'])+1
                conn.rpush('count',json.dumps(dict))
            if flag==True:
                return jsonify(code=203, message='请去图片所在相册查看结果')
            return jsonify(code=200, message="success srcnn")
    else:
        rediskey = 'useralbum:' + str(current_user.id)
        albumdictlist = []
        for albumid in conn.smembers(rediskey):
            dict = {}
            albumid=byte2int(albumid)
            album = Photoalbum.query.filter_by(id=albumid).first()
            dict['id'] = album.id
            dict['name'] = album.name
            albumdictlist.append(dict)
        return render_template('superresolution.html', albums=albumdictlist)


@image.route('/compare', methods=['GET', 'POST'])
def compare():
    data = json.loads(request.get_data(as_text=True))
    imgid = data['imgid']
    img = Image.query.filter_by(id=imgid).first()
    orginimg = Image.query.filter_by(id=img.orig_id).first()  # 原图
    if ImageType(img.action) == ImageType.SRCNN:
        return jsonify(code=200, message='和原图进行比较', url=orginimg.url)
    else:
        if ImageType(img.action)==ImageType.UPSCALE_2X:
            times = 2  # Upscale_2x
            eimg=Image.query.filter_by(orig_id=img.orig_id, action=ImageType.BICUBIC_UPSCALE_2X.value).first()
            if eimg!=None:
                return jsonify(code=201,url=eimg.url)
        elif ImageType(img.action)==ImageType.UPSCALE_3X:
            times = 3
            eimg = Image.query.filter_by(orig_id=img.orig_id, action=ImageType.BICUBIC_UPSCALE_3X.value).first()
            if eimg != None:
                return jsonify(code=201, url=eimg.url)
        imgContent = fdfs_client.downloadbyBuffer(orginimg.url[len(fdfs_addr):])
        orgimg = cv.imdecode(np.frombuffer(imgContent, np.uint8), cv.IMREAD_COLOR)
        with tf.Session() as sess:
            srcnn = SRCNN(sess, "../srcnn/checkpoint/srcnn_21")
            img = srcnn.upscaling(orgimg, times, False)
        img = Img.fromarray(img)
        f = BytesIO()
        img.save(f, format='PNG')
        f = f.getvalue()
        suffix = orginimg.name[orginimg.name.find('.') + 1:]
        url = fdfs_addr + fdfs_client.uploadbyBuffer(f, suffix)
        imgname = url[url.rfind('/') + 1:]
        if times==3:
            newpic = Image(imgname, url,ImageType.BICUBIC_UPSCALE_3X , orginimg.id, current_user.id, -1)
        elif times==2:
            newpic = Image(imgname, url,ImageType.BICUBIC_UPSCALE_2X , orginimg.id, current_user.id, -1)
        db.session.add(newpic)
        db.session.flush()
        db.session.commit()
        return jsonify(code=201, message='和传统放大方法进行比较', url=newpic.url)


@image.route('/closecompare', methods=['GET', 'POST'])
def closecompare():
    data = json.loads(request.get_data(as_text=True))
    imgid = data['imgid']  # bicubicUpscale_2x
    img = Image.query.filter_by(id=imgid).first()
    if img == None:
        return jsonify(code=201)
    orig_id = img.orig_id
    img = Image.query.filter_by(orig_id=orig_id, action=ImageType.BICUBIC_UPSCALE_3X.value).first()
    if img==None:
        img = Image.query.filter_by(orig_id=orig_id, action=ImageType.BICUBIC_UPSCALE_2X.value).first()
    if img == None:
        return jsonify(code=202)
    else:
        img = Image.query.filter_by(id=img.id).first()
        fdfs_client.delete(img.url[len(fdfs_addr):])
        db.session.delete(img)
        db.session.commit()
        return jsonify(code=200)
