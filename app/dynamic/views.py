from flask import *
from flask_login import login_required, current_user
from . import dynamic
from app import db
from app.models import Dynamic,Image,Comment,User
from app import fdfs_client,fdfs_addr

@dynamic.route("/adddynamic", methods={'get', 'post'})
@login_required
def index():
    if request.method == 'POST':
        content = request.values.get('dynamiccontent').strip()
        dynamic = Dynamic(content)
        db.session.add(dynamic)
        db.session.flush()
        db.session.commit()
        files=request.files.getlist('dynamicimg')
        for f in files:
            filename=f.filename
            f = f.read()
            suffix = filename[filename.find('.') + 1:]
            url = fdfs_addr + fdfs_client.uploadbyBuffer(f, suffix)
            name = url[url.rfind('/') + 1:]
            img = Image(name, url, 'Origin', -1, current_user.id, dynamic.id)
            db.session.add(img)
        db.session.commit()
        return redirect('/')
    else:
        return render_template('adddynamic.html')

@dynamic.route("/more", methods={'get', 'post'})
def more():
    data = json.loads(request.get_data(as_text=True))
    id = data['id']
    dynamic=Dynamic.query.filter_by(id=id).first()
    return jsonify(code=200,content=dynamic.content)

@dynamic.route("/comment", methods={'get', 'post'})
def comment():
    if isinstance(current_user.is_anonymous, bool):
        return jsonify(code=400,message='用户尚未登录，无法评论')
    data = json.loads(request.get_data(as_text=True))
    type=data['type']
    id = data['id']
    content = data['content']
    userid = data['userid']
    if type=='dynamic':
      comment=Comment(content,current_user.id,2,id)
      db.session.add(comment)
      db.session.flush()
      db.session.commit()
      return jsonify(code=200,username=current_user.nickname,userid=current_user.id,content=content,commentid=comment.id)
    else:
      if int(userid)==current_user.id:
          return jsonify(code=400,message='用户不能回复自己')
      actoruser=User.query.filter_by(id=userid).first()
      comment = Comment(content, current_user.id, 3, id)
      db.session.add(comment)
      db.session.commit()
      return jsonify(code=201, username=current_user.nickname, userid=current_user.id, content=content,
                     commentid=comment.id,actorname=actoruser.nickname)

@dynamic.route("/deletecomment", methods={'get', 'post'})
def deletecomment():
    data = json.loads(request.get_data(as_text=True))
    commentid = data['commentid']
    comment = Comment.query.filter_by(id=commentid).first()
    db.session.delete(comment)
    db.session.commit()
    return jsonify(code=200)