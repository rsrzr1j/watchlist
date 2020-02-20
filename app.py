from flask import Flask
from flask import url_for

app=Flask(__name__)

@app.route('/')
def hello():
	return 'Hello'

@app.route('/user/<name>')
def user_page(name):
	return '<h1>User :%s</h1>' % name

@app.route('/test')
def test_url_for():
	#下面是一些调用示例
	print(url_for('hello'))
	print(url_for('user_page',name='gali'))
	print(url_for('user_page',name='peter'))
	# 下面这个调用传入了多余的关键字参数，它们会被作为查询字符串附加到 URL 后面。
	print(url_for('test_url_for',name=2))
	return "Test page,please check them in your cmdline"