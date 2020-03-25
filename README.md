# 配置及运行

## 配置虚拟环境并安装第三方依赖

```bash
python3 -m venv venv
pip install -r requirements.txt
# 运行完上面的，如果在MacOS出现这样的错误Error: pg_config executable not found. 就安装下面的 
brew install postgresql
# CentOS服务器出错则是下面的（https://stackoverflow.com/a/27043037/4493393）
yum install -y postgresql postgresql-devel python-devel
```
##  flask 脚本
因为在虚拟环境中安装 Flask 时会同时安装 flask 脚本
flask 命令由 Flask 安装，而不是你的应用。为了可以使用，它必须被告知可以在哪里找到你的应用。怎么告知呢？终端输入`export FLASK_APP=flasky.py`再输入`flask run`即可启动服务器
即FLASK_APP 环境变量用于定义如何载入应用，详见：https://dormousehole.readthedocs.io/en/latest/cli.html
假如你的 `flasky.py` 文件里有自动初始化数据库的deploy命令，那么可以这么运行

``` bash
export FLASK_APP=flasky.py
flask deploy
```

每次输入含flask的命令你都先要输这个`export FLASK_APP=flasky.py`命令是不是很烦？
没关系，如果嫌麻烦的话就在根目录新建一个`.env`文件然后输入以下敏感信息内容：（也可以`vim .env`然后输入`export FLASK_APP=flasky.py`保存）

``` bash
FLASK_APP=flasky.py
EMAIL=1111@qq.com
DATABASE_PASSWORD=12345678
# 如果想监听文件修改自动刷新可以加上这个
FLASK_DEBUG=1
```
待解决问题：其他变量可以设置，但是直接flask run还是不行
## 请务必设置.env文件上传路径！

此路径存放上传的图片，是个文件夹，一定要存在！

比如我的MacOS是：`UPLOAD_FOLDER='/Users/pan/Downloads/imagepath/'`

CentOS是：`UPLOAD_FOLDER='/var/www/html/image'`

## 初始化数据库

在数据库迁移工具生成的`migrations`不存在的情况下，需要初始化、迁移、升级数据库：

```bash
export FLASK_APP=flasky.py
#由于现在已经有了历史迁移记录文件夹migration，所以你第一次要flask deploy而不需flask db init：
flask deploy
# init初始化仅在第一次，即`migrations`文件夹不存在的时候执行！！！
flask db init
# 每次数据库模型更改时，只需重复migrate和upgrade命令，Initial migration可以换成自己的注释
flask db migrate -m "new table sticker"
flask db upgrade
```

如果升级数据库出问题，删掉数据库后要`flask deploy`



安装所有依赖

``` bash
pip install -r requirements.txt
```

## CentOS的nginx设置

假设我的域名是`example.com`

修改`/etc/nginx/nginx.conf`文件，这里我没用域名的根目录`example.com`，而是`example.com/sticker`：

``` bash
        location /sticker/ 
        {
            proxy_pass http://localhost:5000;
            proxy_set_header   Host    $host;
            proxy_set_header   X-Real-IP   $remote_addr;
            proxy_set_header   X-Forwarded-For $proxy_add_x_forwarded_for;
        }
```

CentOS 安装图片压缩工具做略缩图：
``` bash
yum install ImageMagick
```

## 运行Flask后台服务

``` bash
#默认5000端口
export FLASK_APP=flasky.py
flask run
```


模板渲染的主页：http://127.0.0.1:5000/sticker

API表情主页：http://127.0.0.1:5000/static/s.html

API上传表情：http://127.0.0.1:5000/static/sadd.html

# 后期更新维护及自定义

若想修改数据库表字段，需要更新`models.py`和`manage.py`里的东东，然后`flask db migrate -m "Initial migration" && flask db upgrade`，
注意！！！如果此时出现了`sqlite3.OperationalError) database is locked`错误，请把你的断点走完，再执行`flask db upgrade`

数据库的字段修改：

```bash
# 如果flask db downgrade 出了问题，那么
flask db history
5ae48b37ae9e -> 7d57677c6b19 (head), sticker click num
51f5ccfba190 -> 5ae48b37ae9e, sticker init
修改sqlite数据库的的`alembic_version`值到上一个值`5ae48b37ae9e`
然后删除`migrations/versions`文件夹里面最新的py文件就行
```



## 参考资料

flask-sqlalchemy使用：http://www.pythondoc.com/flask-sqlalchemy/queries.html

# 其他

VSCode调试配置：https://youtu.be/UXqiVe6h3lA

4 个顶级文件夹

• Flask 程序一般都保存在名为 app 的包中;
• 和之前一样，migrations 文件夹包含数据库迁移脚本;
• 单元测试编写在 tests 包中;
• 和之前一样，venv 文件夹包含 Python 虚拟环境。

同时还创建了一些新文件:
requirements.txt 列出了所有依赖包，便于在其他电脑中重新生成相同的虚拟环境;
生成依赖文件`pip freeze >requirements.txt`


config.py 存储配置;

manage.py 用于启动程序以及其他的程序任务。

```bash
# 一下子升级所有可升级的第三方库
pip list --outdated --format=freeze | grep -v '^\-e' | cut -d = -f 1  | xargs -n1 pip install -U
```





# 理解



```python
class User(UserMixin, db.Model):
    posts = db.relationship('Post', backref='author', lazy='dynamic')

class Post(db.Model):
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    
    
#contains()    
#venv/lib/python3.7/site-packages/sqlalchemy/sql/operators.py

#offset()
#venv/lib/python3.7/site-packages/sqlalchemy/orm/query.py:3141

#all()
#venv/lib/python3.7/site-packages/sqlalchemy/orm/query.py:3227



```

