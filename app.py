from flask import Flask,render_template
from flask import url_for
#导入扩展
from flask_sqlalchemy import SQLAlchemy
import os,sys

app=Flask(__name__)
#初始化扩展，传入程序实例
db=SQLAlchemy(app)
#为了设置 Flask、扩展或是我们程序本身的一些行为，
#我们需要设置和定义一些配 置变量。Flask 提供了一个统一的接口来写入和获取这些配置变
#量: Flask.config 字典。
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:////'+os.path.join(app.root_path,'data.db')
#sqlite:////是SQLite数据库的绝对地址，不同的dbms有不同的地址
#关闭对模型修改的监控
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
#在扩展类实例化前加载配置
db = SQLAlchemy(app)

#创建数据库模型
class User(db.Model):#表名将会是user，自动生成，小写处理
	#主键
	id=db.Column(db.Integer,primary_key=True)
	#名字
	name=db.Column(db.String(20))

class Movie(db.Model):#表名将会是movie
	id=db.Column(db.Integer,primary_key=True)
	title=db.Column(db.String(60))#电影标题
	year=db.Column(db.String(4))

#自定义命令 initdb
import click
@app.cli.command() #注册为命令
#设置选项
@click.option('--drop',is_flag=True,help='Create after drop.')
def initdb(drop):
	"""Initialize the database."""
	if drop:#判断是否输入了选项
		db.drop_all()
	db.create_all()
	click.echo('Initialized database.')#输出提示信息


#创建自定义命令 forge 以便创建虚拟数据
@app.cli.command()
def forge():
	'''Generate fake data.'''
	db.create_all()

	#全局的两个变量移动到此处
	#准备虚拟数据
	name='yf zhang'
	movies=[
		{'title': 'My Neighbor Totoro', 'year': '1988'},
		{'title': 'Dead Poets Society', 'year': '1989'},
		{'title': 'A Perfect World', 'year': '1993'},
		{'title': 'Leon', 'year': '1994'},
		{'title': 'Mahjong', 'year': '1996'},
		{'title': 'Swallowtail Butterfly', 'year': '1996'}, 
		{'title': 'King of Comedy', 'year': '1999'}, 
		{'title': 'Devils on the Doorstep', 'year': '1999'},
		{'title': 'WALL-E', 'year': '2008'},
		{'title': 'The Pork of Music', 'year': '2012'},
	]
	user=User(name=name)
	db.session.add(user)
	for m in movies:
		movie=Movie(title=m['title'],year=m['year'])
		db.session.add(movie)
	db.session.commit()
	click.echo('Forge Done.')
	
@app.route('/')
def index():
	user=User.query.first() #读取用户记录
	movies=Movie.query.all() #读取所有电影记录
	return render_template('index.html',name=user,movies=movies)
