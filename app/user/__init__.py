from flask import Blueprint
user = Blueprint('user', __name__)
from flask_login import LoginManager
from app import app

# 登录的实例
login_manager = LoginManager()
# 登录失败跳转的界面
login_manager.login_view = '/user/regloginpage'
# 跳转到登录页面显示的信息
login_manager.init_app(app)

from .views import *