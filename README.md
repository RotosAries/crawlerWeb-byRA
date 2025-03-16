# 项目概述

本项目是一个简单的网页爬取工具，包含前端和后端两部分。前端基于Vue.js实现爬取界面，后端基于FastAPI实现爬取逻辑。用户可以通过前端输入目标网址，后端执行爬取并返回结果。

## 项目开发环境
- 系统开发环境：Ubuntu 24.04.1 LTS
- 前端开发环境：
	- node.js v22.14.0
	- npm 10.9.2
- 后端开发环境：
	- Python 3.12.3
	- pip 24.0

## 技术栈

### 前端
- **Vue.js**: 前端框架
- **axios**: HTTP请求库
- **vue-router**: 路由管理
### 后端

- **FastAPI**: 后端框架
- **crawl4ai**: 网页爬取库
- **uvicorn**: ASGI服务器

## 项目结构

```
my_crawler/

├── backend/              # 后端代码

│   ├── app/              # 应用代码

│   │   ├── api/          # API路由

│   │   ├── config/       # 配置文件

│   │   ├── core/         # 核心逻辑

│   │   ├── models/       # 数据模型

│   │   ├── utils/        # 工具模块

│   │   ├── main.py       # 应用入口文件

│   │   └── ...           # 其他文件

│   └── README.md         # 后端文档

|   └── requirements.txt  # 后端依赖列表

├── frontend/             # 前端代码

│   ├── src/              # 源代码

│   │   ├── assets/       # 静态资源

│   │   ├── components/   # 通用组件

│   │   ├── router/       # 路由配置

│   │   ├── views/        # 页面组件

│   │   ├── App.vue       # 主组件

│   │   └── main.js       # 入口文件

│   └── README.md         # 前端文档

│   └── ...           # 其他文件

└── README.md             # 项目整体文档
```

## 功能说明

### 前端
更多详情请查看[前端README文件](frontend/README.md)
1. **网页爬取**：
	- 用户输入目标网址，点击“开始爬取”按钮后，应用通过`axios`向后端发送请求获取网页内容。
	- 支持URL验证和处理，确保输入的网址有效。
	- 爬取结果以文本形式展示，并提供下载功能，将结果保存为Markdown文件。

2. **错误处理**：
	- 当爬取失败或请求超时时，应用会显示错误提示信息。
### 后端
更多详情请查看[后端README文件](backend/README.md)
1. **路由配置**：
	- 定义根路由`/`，返回欢迎消息。
	- 定义爬虫路由`/api/crawl`，接收前端请求并执行爬取逻辑。

2. **爬虫逻辑**：
	- 使用`crawl4ai`库执行网页爬取。
	- 支持URL验证、处理以及错误提示。

3. **配置管理**：
	- 使用`ConfigLoader`类加载和管理配置文件。
	- 支持实时监听配置文件变化并自动重新加载。

## 运行说明

### 前端

1. 确保已安装Node.js和npm。
2. 在`frontend/`目录下运行以下命令：

```bash
npm install
npm run serve
```

3. 访问`http://localhost:8080`即可使用应用。

### 后端

1. 确保已安装Python和pip，推荐使用虚拟环境。
2. 在`backend/`目录下运行以下命令：

```bash
pip install -r requirements.txt
uvicorn app.main:app
```

3. 访问`http://localhost:8000`即可使用API。

## 注意事项

- 请确保后端服务已启动，并配置正确的API地址（默认指向`http://localhost:8000/api`）。
- 请确保配置文件`backend/app/config/config.json`存在。