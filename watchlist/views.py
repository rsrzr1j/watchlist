from flask_login import login_required,current_user
from flask import render_template,request,redirect,flash,url_for

from watchlist import app,db
from watchlist.models import User,Movie

#主页
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
		flash('Item created.')#显示成功创建的提示
		return redirect(url_for('index'))
	user=User.query.first() #读取用户记录
	movies=Movie.query.all() #读取所有电影记录
	return render_template('index.html',movies=movies)

#编辑电影条目
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
from flask_login import logout_user
@app.route('/logout')
@login_required #用户视图保护
def logout():
	logout_user()#登出用户
	flash('Goodbye.')
	return redirect(url_for('index'))

#支持设置用户名字
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
