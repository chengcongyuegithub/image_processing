from app import conn,db,fdfs_addr,fdfs_client,tf,cv
import numpy as np
from app.models import Image
from flask_login import current_user
from PIL import Image as Img
from srcnn.model import SRCNN
from io import BytesIO
import sys
import time
# 大型任务1：批量删除大量的图片
def deleteinbatch(userid,albumid):
    rediskey = 'album:' + str(userid) + ':' + str(albumid)
    for imgid in conn.zrange(rediskey, 0, sys.maxsize, desc=True, withscores=False, score_cast_func=float):
        img = Image.query.filter_by(id=imgid).first()
        # 删除mysql
        fdfs_client.delete(img.url[len(fdfs_addr):])
        db.session.delete(img)
        db.session.commit()
        # 删除redis
        conn.zrem(rediskey, imgid)
    return True
# 大型任务2：SRCNN处理大型图片，设置为长宽有超过900的
def srcnn_process(imgid,albumid,userid):
    img = Image.query.filter_by(id=imgid).first()
    suffix = img.name[img.name.find('.') + 1:]
    imgContent = fdfs_client.downloadbyBuffer(img.url[len(fdfs_addr):])
    img = cv.imdecode(np.frombuffer(imgContent, np.uint8), cv.IMREAD_COLOR)
    g1 = tf.Graph()
    with tf.Session(graph=g1) as sess:
        srcnn = SRCNN(sess, "../srcnn/checkpoint")
        img = srcnn.superresolution(img)
    img = Img.fromarray(img)
    f = BytesIO()
    img.save(f, format='PNG')
    f = f.getvalue()
    # 保存并上传数据库
    url = fdfs_addr + fdfs_client.uploadbyBuffer(f, suffix)
    imgname = url[url.rfind('/') + 1:]
    newimg = Image(imgname, url, 'SRCNN',imgid,userid,-1)
    db.session.add(newimg)
    db.session.flush()
    db.session.commit()
    if albumid == None or albumid == '' or albumid == '1':
        rediskey = 'album:' + str(userid) + ':1'
    else:
        rediskey = 'album:' + str(userid) + ':' + albumid
    conn.zadd(rediskey, {newimg.id: time.time()})
    return True
