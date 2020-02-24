'''包构造文件，创建程序实例'''
'''创建程序实例，初始化扩展的代码放到此处'''
import os,sys
from flask import Flask
#导入扩展
from flask_sqlalchemy import SQLAlchemy
#初始化Flask-Login
#这个扩展的初始化步骤稍微有些不同，除了实例化扩展类之外，我们还要实现一 个“用户加载回调函数
from flask_login import LoginManager

app=Flask(__name__)
#设置签名所需的密钥,用于flash
app.config['SECRET_KEY'] = 'dev'#
#初始化扩展，传入程序实例
#为了设置 Flask、扩展或是我们程序本身的一些行为，
#我们需要设置和定义一些配 置变量。Flask 提供了一个统一的接口来写入和获取这些配置变
#量: Flask.config 字典。
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:////'+os.path.join(os.path.dirname(app.root_path),'data.db')
#sqlite:////是SQLite数据库的绝对地址，不同的dbms有不同的地址
# 注意更新这里的路径，把 app.root_path 添加到 os.path.dirname() 中
# 以便把文件定位到项目根目录

#关闭对模型修改的监控
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False

#在扩展类实例化前加载配置
db = SQLAlchemy(app)

login_manager=LoginManager(app) #实例化扩展类

@login_manager.user_loader
def load_user(user_id):#创建用户加载回调函数，接受用户id作为参数
	from watchlist.models import User
	user=User.query.get(int(user_id)) #用id作文User模型的主键查询对应的用户
	return user #返回用户对象

login_manager.login_view='login'#为了让用户认证的重定向操作正确执行



#模板上下文处理函数
#对于多个模板内都需要使用的变量，
#我们可以使用 app.context_processor 装 饰器注册一个模板上下文处理函数	
@app.context_processor
def inject_user():#函数名可以随意修改
	from watchlist.models import User
	user=User.query.first()
	return dict(user=user) # 需要返回字典，等同于return {'user': user}

#在构造文件中，为了让视图函数、
#错误处理函数和命令函数注册到程序实例上，我 们需要在这里导入这几个模块
#因为这几个模块同时也要导入构造文件中的程 序实例，为了避免循环依赖
#导入语句放到构造文件的结尾

from watchlist import views,errors,commands
