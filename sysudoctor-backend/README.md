# SysUDoctor - 后端配置与工具

## 项目说明
这是系统医生项目的后端配置部分，包含服务器配置、开发工具、文档和扩展功能。

## 项目结构
```
sysudoctor-backend/
├── conf/                   # 高级配置文件
│   ├── fastcgi.conf       # FastCGI 配置
│   ├── fastcgi_params     # FastCGI 参数
│   ├── scgi_params        # SCGI 参数  
│   ├── uwsgi_params       # uWSGI 参数
│   ├── koi-utf           # 字符编码配置
│   ├── koi-win           # 字符编码配置
│   └── win-utf           # 字符编码配置
├── contrib/               # 贡献工具和扩展
│   ├── geo2nginx.pl      # IP 地理位置转换脚本
│   ├── unicode2nginx/    # Unicode 映射工具
│   └── vim/              # Vim 编辑器支持
│       ├── ftdetect/     # 文件类型检测
│       ├── ftplugin/     # 文件类型插件
│       ├── indent/       # 缩进规则
│       └── syntax/       # 语法高亮
├── docs/                  # 项目文档
│   ├── CHANGES           # 版本变更记录 (英文)
│   ├── CHANGES.ru        # 版本变更记录 (俄文)
│   ├── LICENSE           # 许可证文件
│   ├── README            # 基础说明
│   ├── OpenSSL.LICENSE   # OpenSSL 许可证
│   ├── PCRE.LICENCE      # PCRE 许可证
│   └── zlib.LICENSE      # zlib 许可证
└── temp/                  # 临时文件目录
    ├── client_body_temp/  # 客户端请求体临时文件
    ├── fastcgi_temp/     # FastCGI 临时文件
    ├── proxy_temp/       # 代理临时文件
    ├── scgi_temp/        # SCGI 临时文件
    └── uwsgi_temp/       # uWSGI 临时文件
```

## 主要功能
1. **服务器配置管理**
   - FastCGI/SCGI/uWSGI 协议支持
   - 字符编码处理
   - 代理服务配置

2. **开发工具**
   - Perl 脚本工具
   - Vim 编辑器支持
   - 地理位置处理

3. **文档管理**
   - 完整的版本变更记录
   - 许可证文件管理
   - 项目说明文档

## 技术特性
- 支持多种 CGI 协议
- 国际化字符编码支持
- 完整的开发者工具链
- 详细的版本控制和文档

## 配置说明
1. **FastCGI 配置**：支持 PHP 等动态语言
2. **代理配置**：支持负载均衡和反向代理
3. **字符编码**：支持多语言环境
4. **临时目录**：处理各种临时文件

## 开发工具
- **geo2nginx.pl**：地理位置数据转换
- **unicode2nginx**：Unicode 字符映射
- **vim 支持**：完整的 nginx 配置语法高亮

## Nginx 版本信息
基于 nginx 1.22.0 版本，包含：
- OpenSSL 支持
- PCRE 正则表达式支持  
- zlib 压缩支持

## 协作说明
- 本仓库专注于服务器配置和后端工具
- 前端界面和静态资源由另一个仓库负责
- 提供完整的服务器运行环境和配置支持
