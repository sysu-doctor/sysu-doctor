# 设计文档

## 项目结构

| - AIDoctor

​    | - blueprints    各个模块的实现

​        | - doctor.py

​	| - user.py

​    | - app.py    启动

​    | - models.py    实体类

​    | - config.py    配置

​    | - exts.py    拓展（目前用来初始化数据库，意义未明）

​    | - utils.py    工具函数，工具类

​    | - vo.py    视图类（返回给前端的数据封装）

​    | - requirements.txt    依赖管理

​    | - .env    用于存储**应用级配置和敏感信息**

​    | - .flaskenv    专门用于存储 **Flask 框架自身**的配置变量

app.py

使用程序工厂函数，在这里完成配置环境，蓝本注册，钩子函数注册等

运行项目可以在终端输入flask run即可

使用pycharm运行项目，则需要配置一下

![image-20250503220856342](./readme.assets/image-20250503220856342.png)

![image-20250503220955996](./readme.assets/image-20250503220955996.png)

保证各个文件都是项目的根目录

.env用于存储**应用级配置和敏感信息**，比如密钥，数据库连接URI，以键值对格式保存，在程序运行时通过os.getenv[“key”]获取，这个一般不会用git版本控制，像DEV_DB_URI和TEST_DB_URI在开发时候每个人都要改成自己的电脑上的数据库

```
JWT_SECRET_KEY='Drmhze6EPcv0fN_81Bj-nA'
JWT_TOKEN_LOCATION="headers"
DEV_DB_URI="mysql+pymysql://root:123456@127.0.0.1:3306/doctor?charset=utf8"
TEST_DB_URI="mysql+pymysql://root:123456@127.0.0.1:3306/doctor?charset=utf8"
```

.flaskenv专门用于存储 **Flask 框架自身**的配置变量，这里只用来规定了启动函数的位置，这两个文件需要在github拉取下来后自己创建。

```
FLASK_APP=app.py
```

config.py使用类组织配置（一般不需要修改）

```py
import os

class Config:
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'secret string')
    JWT_TOKEN_LOCATION = os.getenv('JWT_TOKEN_LOCATION', 'headers')

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.getenv('DEV_DB_URI', 'sqlite:///database.db')

class TestConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.getenv('TEST_DB_URI', 'sqlite:///database.db')

config = {
    'development': DevelopmentConfig,
    'test': TestConfig,
    'default': DevelopmentConfig
}
```

utils.py是放工具的，比如这个返回结构的封装，如何使用下面再说



```python
# 返回格式
class Result:
    def __init__(self, code, msg, data):
        self.code = code
        self.msg = msg
        self.data = data

    @staticmethod
    def success(data=None):
        return Result(1, "", data)

    @staticmethod
    def error(msg):
        return Result(0, msg, None)

    def to_dict(self):
        return {
            "code": self.code,
            "msg": self.msg,
            "data": self.data
        }
```

blueprints包就是放各个模块，比如user.py，这里也可以确定一下开发的大致流程，分为三个步骤：从请求中获取数据，（处理后）查询数据库，（处理）后返回给前端。

```python
bp = Blueprint("user", __name__, url_prefix='/user')


@bp.route('/login', methods=['POST'])
def login():
    # 读取请求数据
    data = request.get_json()
    phone = data.get('phone')
    password = data.get('password')

    # 查询数据库
    user = UserModel.query.filter_by(phone=phone).one_or_none()

    # 数据处理
    if not user:
        return jsonify(Result.error("该手机号未注册！").to_dict())
    if password != user.password:
        return jsonify(Result.error("密码错误！").to_dict())

    # 登录成功，生成JWT令牌
    token = create_access_token(identity=user.id, additional_claims={"role":"user"})

    #返回结果
    login_vo = LoginVO(id=user.id, name=user.name, token=token, role="user")
    result = Result.success(login_vo.to_dict())
    return jsonify(result.to_dict())
```

jsonify可以将字典或者可序列化的对象转为JSON格式，使用Result返回响应时，如果要传入data，先将data转化为字典，再传给Result的静态方法，再将Result转为字典（或许有优化空间）。下面是成功JSON化的示例。

```json
{
    "code":1,
    "msg":"",
    "data":{
        "id":1,
        "name":"Tom",
        "role":"user"
    }
}
```

vo.py是放返回给视图数据的对象的，也就是传给Result的静态方法的data的封装，基于上面可知，一定要实现to_dict方法。

```python
class LoginVO:
    def __init__(self, id, name, role, token):
        self.id = id
        self.name = name
        self.role = role
        self.token = token
    def to_dict(self):
        return {"id": self.id, "name": self.name, "role": self.role, "token": self.token}
```

requirements.txt则记录了项目依赖的库，直接在终端输入即可，在pycharm的开发环境下，当缺失或新增依赖库时，都会有提示，让它帮我们修改即可。

```
pip install -r requirements.txt
```

因此我们的主要工作就是实现蓝图里的模块。