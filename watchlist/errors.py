from flask import render_template
from watchlist import app
@app.errorhandler(404) #传入要处理的错误代码
def page_not_found(e): #接受异常对象作文参数
	return render_template('errors/404.html'),404
	#返回模板和状态码,
	#普通的视图函数之所以不用写出状态码，是因为默认会使用 200 状态码

