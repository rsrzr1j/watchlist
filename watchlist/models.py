from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from watchlist import db
#创建数据库模型
class User(db.Model,UserMixin):#表名将会是user，自动生成，小写处理,
#并让存储用户的 User 模型类继承 Flask-Login 提供的 UserMixin 类
#继承这个类会让User类拥有几个用于判断认证状态的属性和方法
	#主键
	id=db.Column(db.Integer,primary_key=True)
	#名字
	name=db.Column(db.String(20))
	username=db.Column(db.String(20))#用户名
	password_hash=db.Column(db.String(128))#密码hash值
	def set_password(self,password):#用来设置密码的方法
		self.password_hash=generate_password_hash(password)
	def validate_password(self,password):
		return check_password_hash(self.password_hash,password)

class Movie(db.Model):#表名将会是movie
	id=db.Column(db.Integer,primary_key=True)
	title=db.Column(db.String(60))#电影标题
	year=db.Column(db.String(4))
