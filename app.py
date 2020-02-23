from flask import Flask,render_template,request,redirect,flash
from flask import url_for
#导入扩展
from flask_sqlalchemy import SQLAlchemy
import os,sys

app=Flask(__name__)
#初始化扩展，传入程序实例
#为了设置 Flask、扩展或是我们程序本身的一些行为，
#我们需要设置和定义一些配 置变量。Flask 提供了一个统一的接口来写入和获取这些配置变
#量: Flask.config 字典。
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:////'+os.path.join(app.root_path,'data.db')
#sqlite:////是SQLite数据库的绝对地址，不同的dbms有不同的地址
#关闭对模型修改的监控
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
#在扩展类实例化前加载配置
db = SQLAlchemy(app)
#设置签名所需的密钥,用于flash
app.config['SECRET_KEY'] = 'dev'#

from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
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

##生成管理员账户
import click
@app.cli.command()
@click.option('--username',prompt=True,help='The username used to login.')
@click.option('--password',prompt=True,hide_input=True,
	confirmation_prompt=True,help='The password used to login.')
def admin(username,password):
	'''Create user.'''
	db.create_all()
	user=User.query.first()
	if user is not None:
		click.echo('Updating user.')
		user.username=username
		user.set_password(password)
	else:
		click.echo('Creating user...')
		user=User(username=username,name='Admin')
		user.set_password(password)
		db.session.add(user)
	db.session.commit()
	click.echo('Done.')


#初始化Flask-Login
#这个扩展的初始化步骤稍微有些不同，除了实例化扩展类之外，我们还要实现一 个“用户加载回调函数
from flask_login import LoginManager
login_manager=LoginManager(app) #实例化扩展类

@login_manager.user_loader
def load_user(user_id):#创建用户加载回调函数，接受用户id作为参数
	user=User.query.get(int(user_id)) #用id作文User模型的主键查询对应的用户
	return user #返回用户对象




#模板上下文处理函数
#对于多个模板内都需要使用的变量，
#我们可以使用 app.context_processor 装 饰器注册一个模板上下文处理函数	
@app.context_processor
def inject_user():#函数名可以随意修改
 user=User.query.first()
 return dict(user=user) # 需要返回字典，等同于return {'user': user}

@app.errorhandler(404) #传入要处理的错误代码
def page_not_found(e): #接受异常对象作文参数
	return render_template('404.html'),404
	#返回模板和状态码,
	#普通的视图函数之所以不用写出状态码，是因为默认会使用 200 状态码

from flask_login import login_required,current_user
@app.route('/',methods=['GET','POST'])
def index():
	if request.method=='POST':#判断请求是否是post
		#获取表单数据
		if not current_user.is_authenticated:#若当前用户未认证
			return redirect(url_for('index'))#目的在于禁止未登陆用户创建新条目
		title=request.form.get('title')#传入表单对应字段的name值
		year=request.form.get('year')
		#验证数据
		if not title or not year or len(year)>4 or len(title)>60:
			flash('Invalid input.')#显示错误提示
			return redirect(url_for('index'))#重定向回主页
		#保存数据到数据库
		movie=Movie(title=title,year=year)#创建记录
		db.session.add(movie) #添加到数据库会话
		db.session.commit()#提交数据库会话
		flash('Iterm created.')#显示成功创建的提示
		return redirect(url_for('index'))
	user=User.query.first() #读取用户记录
	movies=Movie.query.all() #读取所有电影记录
	return render_template('index.html',movies=movies)

#编辑电影条目
login_manager.login_view='login'#为了让用户认证的重定向操作正确执行
@app.route('/movie/edit/<int:movie_id>',methods=['GET','POST'])
@login_required #登陆保护
def edit(movie_id):
	movie=Movie.query.get_or_404(movie_id)
	if request.method=='POST':#处理编辑表单的请求
		title=request.form['title']
		year=request.form['year']
		if not title or not year or len(year)>4 or len(title)>60:
			flash('Invalid input.')
			return redirect(url_for('edit',movie_id=movie_id))
			#重新定向回默认的编辑页面
		#更新数据
		movie.title=title
		movie.year=year
		db.session.commit()
		flash('Item updated.')
		return redirect(url_for('index'))
	return render_template('edit.html',movie=movie)
	#传入被编辑的电影记录

#删除电影条目
@app.route('/movie/delete/<int:movie_id>',methods=['POST'])
#限定只接受POST请求
@login_required#登陆保护
def delete(movie_id):
	movie=Movie.query.get_or_404(movie_id)#获取电影记录
	db.session.delete(movie)
	db.session.commit()
	flash('Item deleted.')
	return redirect(url_for('index'))

#用于显示登陆页面和登陆表单的视图函数
from flask_login import login_user
@app.route('/login',methods=['GET','POST'])
def login():
	if request.method=='POST':
		username=request.form['username']
		password=request.form['password']

		if not username or not password:
			flash('Invalid input.')
			return redirect(url_for('login'))

		user=User.query.first()
		#验证用户名和密码
		if username==user.username and user.validate_password(password):
			login_user(user)#登陆用户
			flash('Login success.')
			return redirect(url_for('index'))#重定向回主页

		flash('Invalid username or password.')#验证失败提示
		return redirect(url_for('login'))
	return render_template('login.html')

#登出操作
from flask_login import login_required,logout_user
@app.route('/logout')
@login_required #用户视图保护
def logout():
	logout_user()#登出用户
	flash('Goodbye.')
	return redirect(url_for('index'))

#支持设置用户名字
from flask_login import login_required,current_user
@app.route('/settings',methods=['GET','POST'])
@login_required
def settings():
	if request.method=='POST':
		name=request.form['name']
		if not name or len(name)>20:
			flash('Invalid input.')
			return redirect(url_for('settings'))
		current_user.name=name
		# current_user 会返回当前登录用户的数据库记录对象
		# 等同于下面的用法
		# user = User.query.first()
		# user.name = name
		db.session.commit()
		flash('Settings updated.')
		return redirect(url_for('index'))
	return render_template('settings.html')
