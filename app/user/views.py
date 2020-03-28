from . import user, login_manager
from app.models import User, Message, Photoalbum
from flask import *
from flask_login import login_user, logout_user, login_required, current_user
from event.event_queue import fireEvent
from event.model import EventType, EventModel, EntityType
from app import db, conn, fdfs_addr, fdfs_client
import hashlib
import random
import time
import sys


@user.route("/myspace")
@login_required
def index():
    followercount, followeecount = followerandeecount(str(current_user.id))
    return render_template('user.html', user=current_user, followercount=followercount, followeecount=followeecount)


@user.route("/follower")
@login_required
def follower():  # 被多少人关注
    list = followerlist(str(current_user.id))
    return render_template('follower.html', followerlist=list)


@user.route("/followee")
@login_required
def followee():  # 关注了多少人
    list = followeelist(str(current_user.id))
    return render_template('followee.html', followeelist=list)


@user.route("/follow", methods={'get', 'post'})
@login_required
def follow():
    data = json.loads(request.get_data(as_text=True))
    userid = data['userid']
    # 构造rediskey
    followerkey = 'follower:1:' + userid  # 有哪些人关注了这个user
    followeekey = 'followee:' + str(current_user.id) + ':1'  # 当前执行操作的人关注了那些人
    conn.zadd(followerkey, {current_user.id: time.time()})
    conn.zadd(followeekey, {userid: time.time()})
    # 发送私信
    fireEvent(EventModel(EventType.FOLLOW, current_user.id, EntityType.USER, userid, userid, {'name':current_user.nickname}))
    return jsonify(code=200)


@user.route("/unfollow", methods={'get', 'post'})
@login_required
def unfollow():
    data = json.loads(request.get_data(as_text=True))
    userid = data['userid']
    # 构造rediskey
    followerkey = 'follower:1:' + userid  # 有哪些人关注了这个user
    followeekey = 'followee:' + str(current_user.id) + ':1'  # 当前执行操作的人关注了那些人
    conn.zrem(followerkey, current_user.id)
    conn.zrem(followeekey, userid)
    return jsonify(code=200)


@user.route("/<userid>")
def otheruser(userid):
    msgflag = True
    # 没有私信的按钮
    if isinstance(current_user.is_anonymous, bool) is False and str(current_user.id) == userid:  # 登录的情况
        return redirect('/user/myspace')
    elif isinstance(current_user.is_anonymous, bool):  # 匿名的情况
        msgflag = False  # 匿名的情况
    user = User.query.filter_by(id=userid).first()
    # 当前用户是否关注的查看的用户
    isfollow = True
    if msgflag:  # 如果不是匿名的情况
        followeekey = 'followee:' + str(current_user.id) + ':1'
        isfollow = conn.zrank(followeekey, userid)
        if isinstance(isfollow, int):
            isfollow = True
        else:
            isfollow = False
    # 当前用户的关注
    followercount, followeecount = followerandeecount(userid)
    return render_template('otheruser.html', user=user, msgflag=msgflag, updateflag=True, followflag=isfollow,
                           followercount=followercount, followeecount=followeecount)


@user.route("/follower<userid>")
def otherfollower(userid):
    nameflag = False
    if isinstance(current_user.is_anonymous, bool) is False and str(current_user.id) == userid:  # 当前用户并且登录的话直接跳转
        return redirect('/user/follower')
    elif isinstance(current_user.is_anonymous, bool):
        nameflag = False
    user = User.query.filter_by(id=userid).first()
    list = followerlist(userid)
    return render_template('follower.html', followerlist=list, nameflag=nameflag, username=user.nickname)


@user.route("/followee<userid>")
def otherfollowee(userid):
    nameflag = True
    if isinstance(current_user.is_anonymous, bool) is False and str(current_user.id) == userid:
        return redirect('/user/followee')
    elif isinstance(current_user.is_anonymous, bool):
        nameflag = False
    user = User.query.filter_by(id=userid).first()
    list = followeelist(userid)
    return render_template('followee.html', followeelist=list, nameflag=nameflag, username=user.nickname)


@user.route("/updateuser", methods={'get', 'post'})
@login_required
def updateuser():
    return render_template('updateuser.html', user=current_user)


@user.route("/upduser", methods={'get', 'post'})
@login_required
def upduser():
    if request.method == 'POST':
        nickname = request.values.get('nickname').strip()
        signature = request.values.get('signature').strip()
        f = request.files['headurl']
        user = User.query.filter_by(id=current_user.id).first()
        user.nickname = nickname
        user.signature = signature
        if f.filename != '':
            filename = f.filename
            f = f.read()
            suffix = filename[filename.find('.') + 1:]
            url = fdfs_addr + fdfs_client.uploadbyBuffer(f, suffix)
            user.head_url = url
        db.session.commit()
    return redirect('/user/myspace')


@user.route('/useralbum')
@login_required
def useralbum():
    rediskey = 'useralbum:' + str(current_user.id)
    albumdictlist = []
    for albumid in conn.smembers(rediskey):
        # 字符的b'1'转化为数字
        dict = {}
        albumid = str(albumid, encoding="utf-8")
        albumid = int(albumid)
        album = Photoalbum.query.filter_by(id=albumid).first()
        dict['id'] = album.id
        dict['name'] = album.name
        dict['introduce'] = album.introduce[0:7]
        dict['front_cover'] = album.front_cover
        dict['lookmore'] = False if len(album.introduce) < 7 else True
        albumdictlist.append(dict)
    followercount, followeecount = followerandeecount(str(current_user.id))
    return render_template('useralbum.html', albumlist=albumdictlist, user=current_user, followercount=followercount,
                           followeecount=followeecount)


@user.route('/regloginpage')
def relogin():
    # 如果用户已经登录,直接跳到主页
    if current_user.is_authenticated:
        return redirect('/')
    loginmsg = ''
    registmsg = ''
    next = request.args.get('next')
    # 是登录的信息
    for m in get_flashed_messages(with_categories=False, category_filter=['login']):
        loginmsg = loginmsg + m
    # 是注册的信息
    for m in get_flashed_messages(with_categories=False, category_filter=['regist']):
        registmsg = registmsg + m
    for m in get_flashed_messages(with_categories=False, category_filter=['next']):
        next = m
    return render_template('login.html', loginmsg=loginmsg, registmsg=registmsg, next=next)


@user.route('/login', methods={'get', 'post'})
def login():
    username = request.values.get('username').strip()
    password = request.values.get('password').strip()
    next = request.values.get('next')
    user = User.query.filter_by(username=username).first()
    dictmsg = dict()
    if next != None and next.startswith('/') > 0:
        dictmsg['next'] = next
    if username == '' or password == '':
        dictmsg['login'] = '用户名和密码不能为空'
        return redirect_with_msg('/user/regloginpage', dictmsg)
    if user == None:
        dictmsg['login'] = '用户名不存在'
        return redirect_with_msg('/user/regloginpage', dictmsg)
    m = hashlib.md5()
    m.update((password + user.salt).encode('utf8'))
    if m.hexdigest() != user.password:
        dictmsg['login'] = '密码错误'
        return redirect_with_msg('/user/regloginpage', dictmsg)
    login_user(user)
    if next != None and next.startswith('/') > 0:
        return redirect(next)
    return redirect('/')


@user.route('/regist', methods={'get', 'post'})
def regist():
    username = request.values.get('username').strip()
    password = request.values.get('password').strip()
    next = request.values.get('next')
    user = User.query.filter_by(username=username).first()
    dictmsg = dict()
    if next != None and next.startswith('/') > 0:
        dictmsg['next'] = next
    if username == '' or password == '':
        dictmsg['regist'] = '用户名和密码不能为空'
        return redirect_with_msg('/user/regloginpage', dictmsg)
    if user != None:
        dictmsg['regist'] = '用户名已经存在'
        return redirect_with_msg('/user/regloginpage', dictmsg)
    salt = ''.join(random.sample('0123456789abcdefghigklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ', 10))
    m = hashlib.md5()
    m.update((password + salt).encode("utf8"))
    password = m.hexdigest()
    user = User(username, password, salt)
    db.session.add(user)
    db.session.commit()
    login_user(user)
    # 默认创建系统相册
    rediskey = 'useralbum:' + str(current_user.id)
    conn.sadd(rediskey, 1)
    # 将注册成功的消息以私信的方式传递给用户
    fireEvent(EventModel(EventType.REGIST, -1, EntityType.USER, current_user.id, current_user.id, {}))
    if next != None and next.startswith('/') > 0:
        return redirect(next)
    return redirect('/')


@user.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@user.route('/islogin', methods={'get', 'post'})
def islogin():
    if current_user.is_authenticated:
        return 'True'
    else:
        return 'False'


@user.route('/message')
@login_required
def message():
    msglist = db.session.query(Message.id, Message.content, Message.createtime, Message.hasRead, User.nickname,
                               User.head_url).outerjoin(User, Message.fromId == User.id).filter(
        Message.toId == current_user.id).order_by(Message.createtime.desc()).limit(10).all()
    msgdiclist = []
    for msg in msglist:
        dict = {}
        dict['id'] = msg.id
        if msg.nickname != None:
            dict['content'] = msg.nickname + ' 对我说: ' + msg.content[0:200]
        else:
            dict['content'] = msg.content[0:200]
        dict['createtime'] = msg.createtime
        dict['hasRead'] = msg.hasRead
        dict['head_url'] = msg.head_url
        msgdiclist.append(dict)
    return render_template('message.html', msglist=msgdiclist)


@user.route('/messagedetail', methods={'get', 'post'})
def messagedetail():
    msgid = request.values.get('msgid').strip()
    message = Message.query.filter_by(id=msgid).first()
    content = ''
    conversationcontentlist = []
    if message.conversationId == '-1':  # 如果不是对话，则展示当前的长对话
        content = message.content
    else:  # 如果是对话的话，则展示全部的对话信息
        fromId = message.conversationId[0:message.conversationId.find('to')]
        toId = message.conversationId[message.conversationId.find('to') + 2:]
        if str(current_user.id) == fromId:
            otherUser = User.query.filter_by(id=toId).first()
        else:
            otherUser = User.query.filter_by(id=fromId).first()
        conversation = Message.query.filter_by(conversationId=message.conversationId).order_by(
            Message.createtime.desc()).all()
        for con in conversation:
            if con.toId == current_user.id:
                conversationcontentlist.append(otherUser.nickname + ' 对我说: ' + con.content)
            else:
                conversationcontentlist.append('我对 ' + otherUser.nickname + ' 说:' + con.content)
    return render_template('messagedetail.html', content=content, conversation=conversationcontentlist)


@user.route('/sendmessage', methods={'get', 'post'})
@login_required
def sendmessage():
    nickname = request.values.get('nickname').strip()
    return render_template('sendmessage.html', nickname=nickname)


@user.route('/sendmsg', methods={'get', 'post'})
@login_required
def sendmsg():
    data = json.loads(request.get_data(as_text=True))
    userid = data['userid']
    content = data['content']
    message = Message(current_user.id, int(userid), content)
    db.session.add(message)
    db.session.commit()
    return jsonify(code=200, message='信息已经发送')


@user.route('/message/isread', methods={'get', 'post'})
@login_required
def isread():
    data = json.loads(request.get_data(as_text=True))
    msgid = data['msgid']
    msg = Message.query.filter_by(id=msgid).first()
    msg.hasRead = 1
    db.session.commit()
    print(current_user)
    return jsonify(code=200, message='信息已读')

# 计算关注和被关注数量
def followerandeecount(userid):
    followerkey = 'follower:1:' + userid  # 有哪些人关注了这个user
    followeekey = 'followee:' + userid + ':1'  # 当前执行操作的人关注了那些人
    followeecount = conn.zcount(followeekey, 0, sys.maxsize)
    followercount = conn.zcount(followerkey, 0, sys.maxsize)
    return followercount, followeecount


# 关注列表
def followerlist(userid):
    followerkey = 'follower:1:' + userid
    followerdictlist = []
    for userid in conn.zrange(followerkey, 0, sys.maxsize, desc=True, withscores=False, score_cast_func=float):
        dict = {}
        userid = str(userid, encoding="utf-8")
        userid = int(userid)
        user = User.query.filter_by(id=userid).first()
        dict['id'] = userid
        dict['name'] = user.nickname
        dict['url'] = user.head_url
        followerdictlist.append(dict)
    return followerdictlist


# 被关注列表
def followeelist(userid):
    followeekey = 'followee:' + userid + ':1'
    followeelist = []
    for userid in conn.zrange(followeekey, 0, sys.maxsize, desc=True, withscores=False, score_cast_func=float):
        dict = {}
        userid = str(userid, encoding="utf-8")
        userid = int(userid)
        user = User.query.filter_by(id=userid).first()
        dict['id'] = userid
        dict['name'] = user.nickname
        dict['url'] = user.head_url
        followeelist.append(dict)
    return followeelist


def redirect_with_msg(target, msg):
    for k in msg.keys():
        flash(msg[k], category=k)
    return redirect(target)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)
