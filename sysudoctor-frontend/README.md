# SysUDoctor - 前端部分

## 项目说明
这是系统医生项目的前端部分，包含所有用户界面相关的文件和资源。

## 项目结构
```
sysudoctor-frontend/
├── nginx.exe                # Nginx 服务器执行文件
├── conf/                    # 基础配置文件
│   ├── nginx.conf          # 主配置文件
│   └── mime.types          # MIME 类型配置
├── html/                   # 前端静态资源
│   ├── index.html          # 主页面
│   ├── 50x.html           # 错误页面
│   ├── assets/            # 编译后的资源文件
│   │   ├── *.js           # JavaScript 文件
│   │   └── *.css          # CSS 样式文件
│   ├── *.jpg              # 图片资源
│   ├── *.png              # 图片资源
│   └── vite.svg           # 图标文件
└── logs/                   # 日志文件夹
    ├── access.log
    ├── error.log
    └── nginx.pid
```

## 主要功能模块
基于资源文件分析，前端包含以下功能模块：
- **用户认证** (AuthForm)
- **聊天功能** (Chat, DoctorChat)
- **AI 功能** (AI)
- **医生信息** (DoctorInfo)
- **患者信息** (PatientInfo)
- **挂号系统** (Registration, RegistrationList, RegistrationRecords)
- **主界面** (Main)

## 技术栈
- 前端框架：基于 Vite 构建
- UI 界面：现代化医疗系统界面
- 静态资源：图片、样式、脚本文件
- 服务器：Nginx

## 开发说明
1. 前端资源位于 `html/` 目录
2. 主要配置文件为 `conf/nginx.conf`
3. 静态资源已编译在 `html/assets/` 目录
4. 图片资源包含多个横幅和图标

## 部署说明
1. 确保 nginx.exe 可执行
2. 配置文件已设置代理到本地 5000 端口的后端服务
3. 静态文件服务配置在 80 端口

## 协作说明
- 本仓库专注于前端界面和用户体验
- 后端 API 和服务器配置由另一个仓库负责
- 通过 nginx 反向代理连接前后端
