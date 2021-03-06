from flask import *
from app import app, conn, socketio, emit
from .models import Dynamic, Image, ImageType, User, Comment, Message
from flask_login import current_user
from threading import Lock
import datetime

thread1 = None
thread2 = None
start_time = None
lock = Lock()


@app.route("/")
def index():
    # 动态
    dynamiclist = Dynamic.query.order_by(Dynamic.changetime.desc()).limit(5).all()
    indexlist = []
    for dynamic in dynamiclist:
        dict = showdynamic(dynamic, True)
        indexlist.append(dict)
    return render_template('index.html', indexlist=indexlist)


@app.route("/more", methods=['POST'])
def more():
    data = json.loads(request.get_data(as_text=True))
    offset = data['offset']
    dynamiclist = Dynamic.query.order_by(Dynamic.changetime.desc()).limit(5).offset(int(offset)).all()
    if len(dynamiclist) == 0:
        return jsonify(code=400)
    indexlist = []
    for dynamic in dynamiclist:
        dict = showdynamic(dynamic, True)
        indexlist.append(dict)
    return jsonify(code=200, indexlist=indexlist)


@app.route("/showimage", methods=['POST'])
def showimage():
    img = request.values.get('img')
    return render_template('dynamicimage.html', img=img)


# 错误页面的跳转
@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html')


# 动态的处理
def showdynamic(dynamic, isshowuser):
    dict = {}
    if (isshowuser):
        user = User.query.filter_by(id=dynamic.user_id).first()
        dict['userid'] = user.id
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
    if len(imgs) == 2 and (ImageType(imgs[0].action) == ImageType.UPSCALE_2X or ImageType(
            imgs[0].action) == ImageType.UPSCALE_3X):
        imglist.append(imgs[1].url)
        imglist.append(imgs[0].url)
    else:
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
    return dict


# 通过树的形式获取到评论
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


# 递归
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


@app.route("/statistics")
def statistics():
    return render_template('statistics.html')


def byte2int(id):
    id = str(id, encoding="utf-8")
    id = int(id)
    return id


@socketio.on('connect', namespace='/websocket')
def test_connect():
    # 单例模式创建线程，定时发布消息
    global thread1, thread2
    with lock:
        if thread1 is None:
            thread1 = socketio.start_background_task(target=background_task)
            thread2 = socketio.start_background_task(target=background_task2)

    # 未读信息
    if isinstance(current_user.is_anonymous, bool):
        return
    else:
        # 私信未读
        message = Message.query.filter_by(toId=current_user.id, hasRead=0).all()
        # feed
        # h = a-b if a>b else a+b
        emit('noreadmsg', {'data': '' if len(message) == 0 else len(message)})


# 任务1：定时发送任务
def background_task():
    count = 0
    while True:
        str = conn.lindex('count', -1)  # 取倒数第二个
        if str == None:
            continue
        else:
            dict = eval(str)
            print(dict)
            socketio.emit('count',
                          {'data': dict['time'], 'count': dict['count']},
                          namespace='/websocket')
        socketio.sleep(5)


# 任务2：定时统计使用次数
def background_task2():
    start_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # 开始时间
    conn.rpush('count', json.dumps({'count': 0, 'time': start_time}))
    while True:
        future_time = (datetime.datetime.now() + datetime.timedelta(seconds=+5)).strftime(
            "%Y-%m-%d %H:%M:%S")  # 当前5秒之后的时间
        conn.rpush('count', json.dumps({'count': 0, 'time': future_time}))
        print(conn.llen('count'))
        while conn.llen('count') >= 3:
            conn.lpop('count')
        socketio.sleep(5)
