# 本地开发前

 

## 1.同步远程仓库最新状态

```
# 拉取主分支最新代码（推荐使用 rebase）
git fetch origin
git rebase origin/main
```

## 2.创建新功能分支

假设你需要实现某个功能，如果该功能分支未存在

```
git checkout -b feat/your-feature-name  # 分支命名规范示例：
                                        # feat/patient-crud
                                        # fix/login-validation
```



## 3.检查依赖更新

```
pip install -r requirements.txt  # 安装新增依赖
flask db upgrade               # 执行可能的数据库迁移
```

requirements.txt记录了项目依赖的库，直接在终端输入即可，在pycharm的开发环境下，当缺失或新增依赖库时，都会有提示，让它帮我们修改即可。



# 本地开发过程

## 项目结构

| - AIDoctor

    | - blueprints    各个模块的实现
    
        | - doctor.py
    
        | - user.py
        
        | - doctor_manager.py
    
        | - user_manager.py
    
    | - app.py    启动
    
    | - models.py    实体类
    
    | - config.py    配置
    
    | - exts.py    拓展（目前用来初始化数据库，意义未明）
    
    | - utils.py    工具函数，工具类
    
    | - vo.py    视图类（返回给前端的数据封装）
    
    | - requirements.txt    依赖管理
    
    | - .env    用于存储**应用级配置和敏感信息**
    
    | - .flaskenv    专门用于存储 **Flask 框架自身**的配置变量

app.py

使用程序工厂函数，在这里完成配置环境，蓝本注册，钩子函数注册等

运行项目可以在终端输入flask run即可

使用pycharm运行项目，则需要配置一下

![image-20250503220856342](./readme.assets/image-20250503220856342.png)

![image-20250503220955996](./readme.assets/image-20250503220955996.png)

保证各个文件都是项目的根目录



## **需要自己修改的部分：.env和.flaskenv**

**首先自己创建两个文件.env和.flaskenv**

.env用于存储**应用级配置和敏感信息**，比如密钥，数据库连接URI，以键值对格式保存，在程序运行时通过os.getenv[“key”]获取，这个一般不会用git版本控制

**DEV_DB_URI和TEST_DB_URI在开发时候每个人都要改成自己的电脑上的数据库**

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
    "code":1,    // 1代表成功，0表示失败
    "msg":"",    // 错误信息
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

关于数据库迁移，因为我们做一点设计一点的开发流程，因此在未来难免会遇到数据库变更，因此需要进行数据库迁移，但是经过实践发现，对迁移脚本进行版本控制会有很多莫名其妙的问题，因此我们不对migration下的文件进行版本控制。

如果你刚克隆代码到本地，还没有migrations文件夹，在终端依次执行下面的指令

```
flask db init
flask db migrate
flask db upgrate
```

另外新建数据库后将原始数据导入数据库，如下图，右上角连接到你的数据库后，选中所有语句，点击左上角。

![image-20250510230008826](./github项目开发过程.assets/image-20250510230008826.png)

如果是开发过程，更新数据库，则只需要

```
flask db migrate
flask db upgrate
```

考虑到后续可能会出现多次从github上拉取代码到本地进行同步，然后自己进行开发项目后又上传到仓库的情况，为了规范开发过程中的数据库迁移：

如果你发现同步之后的文件中包含**/migrations**文件夹

**请立即删除/migrations整个文件夹，同时检查自己的数据库表单中是否存在alembic_version这个表，如果有，请你也删除。**

![06491A1660E0882A60D7573AEB135481](./github项目开发过程.assets/06491A1660E0882A60D7573AEB135481.png)

然后按照上面克初次隆代码到本地的教程，依次执行指令，导入数据到数据库中。



**我们的主要工作就是实现蓝图里的模块。**



# 接口测试

前后端的同学都能用Apifox进行接口测试，原理就是模拟另一端发来的请求/响应

使用Apifox进行接口测试

教程【22分钟学会Apifox！2024年的Apifox有什么全新功能？】 https://www.bilibili.com/video/BV1Jc41147xC/?share_source=copy_web&vd_source=1049d130a97c4a4a9c5862ead3e70415

下载Apifox后，可以加入团队：

狐友yWyR 在 Apifox 邀请你加入团队 SYSU-DOCTOR https://app.apifox.com/invite?token=gtkrt8vWVy31mAYjCsCwm

填写：

**接口说明**

**请求参数**

Header参数：一般包括Content-Type。绝大部分功能都是登录后才展示的，所以还需要Authorization

Body参数：接口与前端进行通信的json格式

**返回响应**

可以仿照已有接口



进行运行时，右下角只要出现“200”，即代表测试成功，如果是其他错误代码，例如404,422,500，要么是接口实现写的有问题，要么是在Apifox中的参数写的有问题



# 本地开发完成后

命令行输入

## 1.检查当前修改

```
git status  # 查看已修改/新增的文件
git diff    # 检查具体代码变更（按q退出）
```

## 2.提交代码到本地仓库

例如实现了某一个模块，同时进行了某些修改

```
git add .                          # 添加所有修改
git commit -m "feat: 实现了XXX模块，对XXX、XXX文件进行了修改，注明修改内容"  # 语义化提交信息
```

## 3.同步最新代码

假设你和他人同时开发时：

1. 他人早上提交了`A文件`的修改到远程仓库
2. 你本地也修改了`A文件`但还没同步
3. 此时直接提交会导致冲突

```
git pull origin main --rebase 
```

如果出现冲突：

```
# 手动解决冲突文件后
git add 冲突文件
git rebase --continue
```

## 4.推送分支到仓库

```
git push origin your-branch-name
```

关于Git，推荐下面课程，除了上面的命令行，也可以学着使用pycharm中集成的git

【尚硅谷Git入门到精通全套教程（涵盖GitHub\Gitee码云\GitLab）】 https://www.bilibili.com/video/BV1vy4y1s7k6/?p=32&share_source=copy_web&vd_source=1049d130a97c4a4a9c5862ead3e70415
