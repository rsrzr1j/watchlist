import unittest
from app import app,db,Movie,User,forge,initdb

class WatchlistTestCase(unittest.TestCase):
	
	def setUp(self):
		#更新配置
		app.config.update(
			TESTING=True,#开启测试模式,这样在出错时不会输出多余信息
			SQLALCHEMY_DATABASE_URI='sqlite:///:memory'
			#这会使用SQLite内存型数据库，不会干扰开发时使用的SQLite数据库文件,且速度更快
		)
		#创建数据库和表
		db.create_all()
		#创建测试数据，一个用户，一条电影条目
		user=User(name='Test',username='test')
		user.set_password('123')
		movie=Movie(title='Test Movie Title',year='2019')
		#使用add_all()方法一次添加多个模型实例，传入列表
		db.session.add_all([user,movie])
		db.session.commit()

		self.client=app.test_client()#创建测试客户端,模拟客户端请求
		self.runner=app.test_cli_runner()#创建测试命令运行器,触发自定义命令

	def tearDown(self):
		db.session.remove()#清除数据库会话
		db.drop_all()#删除数据库表

	#测试程序实例是否存在
	def test_app_exist(self):
		self.assertIsNotNone(app)

	#测试程序是否处于测试模式
	def test_app_is_testing(self):
		self.assertTrue(app.config['TESTING'])

	#测试404页面
	def test_404_page(self):
		response=self.client.get('/nothing')#传入目标URL
		data=response.get_data(as_text=True)#获取 Unicode格式的响应主体
		self.assertIn('Page Not Found - 404',data)#判断是否包含预期内容
		self.assertIn('Go Back',data)
		self.assertEqual(response.status_code,404)#判断响应状态码

	#测试主页
	def test_index_page(self):
		response=self.client.get('/')
		data=response.get_data(as_text=True)
		self.assertIn('Test\'s Watchlist',data)
		self.assertIn('Test Movie Title',data)
		self.assertEqual(response.status_code,200)

	#辅助方法，用于登陆用户
	def login(self):
		self.client.post('/login',data=dict(
			username='test',
			password='123'
		),follow_redirects=True)

	#测试创建条目
	def test_create_item(self):
		self.login()

		#测试创建条目操作
		response=self.client.post('/',data=dict(
			title='New Movie',
			year='2019'
		),follow_redirects=True)
		data=response.get_data(as_text=True)
		self.assertIn('Item created.',data)
		self.assertIn('New Movie',data)

		#测试创建条目操作，但电影标题为空
		response=self.client.post('/',data=dict(
			title='',
			year='2019'
		),follow_redirects=True)
		data=response.get_data(as_text=True)
		self.assertNotIn('Item create.',data)
		self.assertIn('Invalid input.',data)

		#测试创建条目操作，但电影年份为空
		response=self.client.post('/',data=dict(
			title='New Movie',
			year=''
		),follow_redirects=True)
		data=response.get_data(as_text=True)
		self.assertNotIn('Item created.',data)
		self.assertIn('Invalid input.',data)

	#测试更新条目
	def test_updata_item(self):
		self.login()

		#测试更新页面
		response=self.client.get('/movie/edit/1')
		data=response.get_data(as_text=True)
		self.assertIn('Edit item',data)
		self.assertIn('Test Movie Title',data)
		self.assertIn('2019',data)

		#测试更新条目操作
		response=self.client.post('/movie/edit/1',data=dict(
			title='New Movie Edited',
			year='2019'
		),follow_redirects=True)
		data=response.get_data(as_text=True)
		self.assertIn('Item updated.',data)
		self.assertIn('New Movie Edited',data)

		#测试更新条目操作，但电影标题为空
		response=self.client.post('/movie/edit/1',data=dict(
			title='',
			year='2019'
		),follow_redirects=True)
		data=response.get_data(as_text=True)
		self.assertNotIn('Item updated.',data)
		self.assertIn('Invalid input.',data)

		#测试更新条目操作，但电影年份为空
		response=self.client.post('/movie/edit/1',data=dict(
			title='New Movie Edited Again',
			year=''
			),follow_redirects=True)
		data=response.get_data(as_text=True)
		self.assertNotIn('Item updated.',data)
		self.assertNotIn('New Movie Edited Again.',data)
		self.assertIn('Invalid input.',data)

	#测试删除条目
	def test_delete_item(self):
		self.login()

		response=self.client.post('/movie/delete/1',follow_redirects=True)
		data=response.get_data(as_text=True)
		self.assertIn('Item deleted.',data)
		self.assertNotIn('Test Movie Title',data)

	#测试登陆保护
	def test_login_protect(self):
		response=self.client.get('/')
		data=response.get_data(as_text=True)
		self.assertNotIn('Logout',data)
		self.assertNotIn('Settings',data)
		self.assertNotIn('<form method=="post">',data)
		self.assertNotIn('Delete',data)
		self.assertNotIn('Edit',data)

	#测试登陆
	def test_login(self):
		response=self.client.post('/login',data=dict(
			username='test',
			password='123'
		),follow_redirects=True)
		data=response.get_data(as_text=True)
		self.assertIn('Login success.',data)
		self.assertIn('Logout',data)
		self.assertIn('Setting',data)
		self.assertIn('Delete',data)
		self.assertIn('<form method="post">',data)

		#测试使用错误密码登陆
		response=self.client.post('/login',data=dict(
			username='test',
			password='456'
		),follow_redirects=True)
		data=response.get_data(as_text=True)
		self.assertNotIn('Login success.',data)
		self.assertIn('Invalid username or password.',data)

		#测试使用错误的用户名登陆
		response=self.client.post('/login',data=dict(
			username='wrong',
			password='123'
		),follow_redirects=True)
		data=response.get_data(as_text=True)
		self.assertNotIn('Login success.',data)
		self.assertIn('Invalid username or password.',data)

		#测试使用空用户名登陆
		response=self.client.post('/login',data=dict(
			username='',
			password='123'
		),follow_redirects=True)
		data=response.get_data(as_text=True)
		self.assertNotIn('Login success.',data)
		self.assertIn('Invalid input.',data)

		#测试使用空密码登陆
		response=self.client.post('/login',data=dict(
			username='test',
			password=''
		),follow_redirects=True)
		data=response.get_data(as_text=True)
		self.assertNotIn("Login success.",data)
		self.assertIn('Invalid input.',data)

	#测试登陆
	def test_logout(self):
		self.login()

		response=self.client.get('/logout',follow_redirects=True)
		data=response.get_data(as_text=True)
		self.assertIn('Goodbye.',data)
		self.assertNotIn('Logout',data)
		self.assertNotIn('Settings', data)
		self.assertNotIn('Delete', data)
		self.assertNotIn('Edit', data)
		self.assertNotIn('<form method="post">', data)

	#测试设置
	def test_settings(self):
		self.login()
		#测试设置页面
		response=self.client.get('/settings')
		data=response.get_data(as_text=True)
		self.assertIn('Settings',data)
		self.assertIn('Your Name',data)
		#测试更新设置
		response = self.client.post('/settings', data=dict(
		name='Grey Li',
		), follow_redirects=True)
		data = response.get_data(as_text=True)
		self.assertIn('Settings updated.', data)
		self.assertIn('Grey Li', data)
		#测试更新设置,名称为空
		response=self.client.post('/settings',data=dict(
			name='',
		),follow_redirects=True)
		data=response.get_data(as_text=True)
		self.assertNotIn('Settings updated.',data)
		self.assertIn('Invalid input.',data)

	#测试虚拟数据
	def test_forge_command(self):
		result=self.runner.invoke(forge)#通过对它调用 invoke() 方法可以执行命令，
		#传入命 令函数对象，或是使用 args 关键字直接给出命令参数列表
		#它的 output 属性返回命令的输出信息
		self.assertIn('Done',result.output)
		self.assertNotEqual(Movie.query.count(),0)

	#测试初始化数据库
	def test_initdb_command(self):
		result=self.runner.invoke(initdb)
		self.assertIn('Initialized database.',result.output)

	#测试初始化管理员账户
	def test_admin_command(self):
		db.drop_all()
		db.create_all()
		#使用 args 关键字直接给出命令参数列表
		result=self.runner.invoke(args=['admin','--username','grey','--password','123'])
		self.assertIn('Creating user...',result.output)
		self.assertIn('Done',result.output)
		self.assertEqual(User.query.count(),1)
		self.assertEqual(User.query.first().username,'grey')
		self.assertTrue(User.query.first().validate_password('123'))

	#测试更新管理员账户
	def test_admin_command_update(self):
		#使用args参数给出完整命令
		result=self.runner.invoke(args=['admin','--username','peter','--password','456'])
		self.assertIn('Updating user...',result.output)
		self.assertIn('Done',result.output)
		self.assertEqual(User.query.count(),1)
		self.assertEqual(User.query.first().username,'peter')
		self.assertTrue(User.query.first().validate_password('456'))

if __name__=='__main__':
	unittest.main()

