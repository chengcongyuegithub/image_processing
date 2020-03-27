from flask import *
from app import app,db
from .models import Dynamic,Image,User
@app.route("/")
def index():
    dynamiclist=Dynamic.query.order_by(Dynamic.changetime.desc()).all()
    indexlist=[]
    for dynamic in dynamiclist:
        dict={}
        dict['time']=dynamic.changetime
        dict['content']=dynamic.content
        dict['id']=dynamic.id
        imgs=Image.query.filter_by(dynamic_id=dynamic.id).all()
        imglist=[]
        for img in imgs:
            imglist.append(img.url)
            if dict.__contains__('name')==False:
                user=User.query.filter_by(id=img.user_id).first()
                dict['name']=user.nickname
                dict['headurl']=user.head_url
        dict['imgs']=imglist
        indexlist.append(dict)
    return render_template('index.html',indexlist=indexlist)