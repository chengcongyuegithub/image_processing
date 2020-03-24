from . import image
from flask import *
from app import fdfs_client, fdfs_addr, db, conn, cv, tf
from app.models import Image
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
        img = Image(name, url, 'Origin', -1, current_user.id, -1)
        db.session.add(img)
        db.session.flush()
        db.session.commit()
        # 添加到相册中，默认是添加到系统相册中
        if albumid == None or albumid == '' or albumid == '1':
            rediskey = 'album:' + str(current_user.id) + ':1'
        else:
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
    if upscalingimg.action != 'Origin':
        return jsonify(code=400, message='此图片为处理过的图片，请选择其他功能')
    upscalingimg = Image.query.filter_by(action='Upscale_' + time, orig_id=imgid).first()
    if upscalingimg != None:
        return jsonify(code=401, message='此图片已经优化过,请在该相册中查找')
    img = Image.query.filter_by(id=imgid).first()
    suffix = img.name[img.name.find('.') + 1:]
    imgContent = fdfs_client.downloadbyBuffer(img.url[len(fdfs_addr):])
    img = cv.imdecode(np.frombuffer(imgContent, np.uint8), cv.IMREAD_COLOR)
    print(img.shape)
    if img.shape[0] > 900 or img.shape[1] > 900:
        return jsonify(code=402, message='该图片尺寸较大，将无法执行放大操作，请选择其他操作')
    # 丢给线程池
    fireEvent(EventModel(EventType.TASK, current_user.id, EntityType.IMAGE, imgid, current_user.id,
                         {'task': 'srcnn_process', 'action': 'Upscale_' + time, 'suffix': suffix, 'albumid': albumid,
                          'time': time}))
    return jsonify(code=200, message='得到的图片较大，稍后以私信的信息通知你')


@image.route('/superresolution', methods=['GET', 'POST'])
def superresolution():
    data = json.loads(request.get_data(as_text=True))
    imgid = data['imgid']
    albumid = data['albumid']
    srcnnimg = Image.query.filter_by(id=imgid).first()
    if srcnnimg.action != 'Origin':
        return jsonify(code=400, message='此图片为处理过的图片，请选择其他功能')
    srcnnimg = Image.query.filter_by(action='SRCNN', orig_id=imgid).first()
    if srcnnimg != None:
        return jsonify(code=401, message='此图片已经优化过,请在该相册中查找');
    img = Image.query.filter_by(id=imgid).first()
    suffix = img.name[img.name.find('.') + 1:]
    imgContent = fdfs_client.downloadbyBuffer(img.url[len(fdfs_addr):])
    img = cv.imdecode(np.frombuffer(imgContent, np.uint8), cv.IMREAD_COLOR)
    print(img.shape)
    if img.shape[0] > 900 or img.shape[1] > 900:  # 大型任务，交给线程池处理
        fireEvent(EventModel(EventType.TASK, current_user.id, EntityType.IMAGE, imgid, current_user.id,
                             {'task': 'srcnn_process', 'action': 'SRCNN', 'suffix': suffix,
                              'albumid': albumid}))
        return jsonify(code=201, message='图片较大，稍后以私信的信息通知你')
    else:  # 小图片直接处理
        with tf.Session() as sess:
            srcnn = SRCNN(sess, "../srcnn/checkpoint")
            img = srcnn.superresolution(img)
        img = Img.fromarray(img)
        f = BytesIO()
        img.save(f, format='PNG')
        f = f.getvalue()
        # 保存并上传数据库
        url = fdfs_addr + fdfs_client.uploadbyBuffer(f, suffix)
        imgname = url[url.rfind('/') + 1:]
        newimg = Image(imgname, url, 'SRCNN', imgid, current_user.id, -1)
        db.session.add(newimg)
        db.session.flush()
        db.session.commit()
        if albumid == None or albumid == '' or albumid == '1':
            rediskey = 'album:' + str(current_user.id) + ':1'
        else:
            rediskey = 'album:' + str(current_user.id) + ':' + albumid
        conn.zadd(rediskey, {newimg.id: time.time()})
        return jsonify(code=200, message="success srcnn")


@image.route('/compare', methods=['GET', 'POST'])
def compare():
    data = json.loads(request.get_data(as_text=True))
    imgid = data['imgid']
    flag = data['flag']
    if flag == False:
        return jsonify(code=400)
    img = Image.query.filter_by(id=imgid).first()
    orginimg = Image.query.filter_by(id=img.orig_id).first()  # 原图
    if img.action == 'SRCNN':
        return jsonify(code=200, message='和原图进行比较', url=orginimg.url)
    else:
        times = img.action[8:9]  # Upscale_2x
        print(times)
        imgContent = fdfs_client.downloadbyBuffer(orginimg.url[len(fdfs_addr):])
        orgimg = cv.imdecode(np.frombuffer(imgContent, np.uint8), cv.IMREAD_COLOR)
        with tf.Session() as sess:
            srcnn = SRCNN(sess, "../srcnn/checkpoint")
            img = srcnn.upscaling(orgimg, int(times), False)
        img = Img.fromarray(img)
        f = BytesIO()
        img.save(f, format='PNG')
        f = f.getvalue()
        suffix = orginimg.name[orginimg.name.find('.') + 1:]
        url = fdfs_addr + fdfs_client.uploadbyBuffer(f, suffix)
        imgname = url[url.rfind('/') + 1:]
        newpic = Image(imgname, url, 'bicubicUpscale_' + times + 'x', orginimg.id, current_user.id, -1)
        db.session.add(newpic)
        db.session.flush()
        db.session.commit()
        return jsonify(code=201, message='和传统放大方法进行比较', url=newpic.url)
