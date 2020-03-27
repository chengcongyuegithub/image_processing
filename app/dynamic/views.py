from flask import *
from flask_login import login_required, current_user
from . import dynamic
from app import db
from app.models import Dynamic,Image,Comment
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

@dynamic.route("/comment", methods={'get', 'post'})
@login_required
def comment():
    data = json.loads(request.get_data(as_text=True))
    dynamicid = data['dynamicid']
    content = data['content']
    Comment(content,2,dynamicid)
    return jsonify(code=200)