# 后端项目概述

本项目是一个基于FastAPI的后端应用，用于实现简单的网页爬取功能。后端负责接收前端请求，执行爬取逻辑，并返回结果。

## 技术栈

- **FastAPI**: 后端框架
- **crawl4ai**: 网页爬取库
- **uvicorn**: ASGI服务器

## 项目结构

```
backend/app/

├── __init__.py          # 包初始化文件

├── main.py              # 应用入口文件，初始化FastAPI实例和路由

├── api/                 # API路由

│   └── routers/         # 路由定义

│       └── crawl.py     # 爬虫路由

├── config/              # 配置文件

│   ├── config.json      # 配置文件

|   └── config.json.bk   # 配置文件备份

├── core/                # 核心逻辑

│   ├── config_loader.py # 配置加载器

│   └── crawler.py       # 爬虫主逻辑

├── dependencies.py      # 依赖注入配置

├── models/              # 数据模型

│   └── schemas.py       # Pydantic模型

└── utils/               # 工具模块

    └── url_utils.py     # URL处理工具
```

## 功能说明

1. **路由配置**：
	- 定义根路由`/`，返回欢迎消息。
	- 定义爬虫路由`/api/crawl`，接收前端请求并执行爬取逻辑。

2. **爬虫逻辑**：
	- 使用`crawl4ai`库执行网页爬取。
	- 支持URL验证、处理以及错误提示。

3. **配置管理**：
	- 使用`ConfigLoader`类加载和管理配置文件。
	- 支持实时监听配置文件变化并自动重新加载。
	- 配置文件`config/config.json`包含以下配置项：
		- **output_format**：数据返回形式，如Markdown等。
		- **content_filter_choice**：选择内容过滤器，如Pruning等。
		- **browser_config**：浏览器配置，如是否启用无头模式、是否启用详细日志等。
		- **crawler_run_config**：爬虫运行配置，如是否仅提取文本、是否缓存、是否检查robots.txt等。
		- **markdown_generator_config**：Markdown生成配置，如是否忽略链接、图片等。
		- **pruning_content_filter_config**：内容过滤配置，如动态阈值设置。
	- 配置文件中的"output_format"目前仅支持如下格式：
		- `html`：返回网页原始的HTML内容。
		- `markdown`：返回网页原始的Markdown内容。
		- `fit_markdown`: 如果应用了内容过滤 （Pruning/BM25），则返回过滤后的Markdown内容，否则为空。
		- `raw_markdown`: 如果应用了内容过滤 （Pruning/BM25），则返回原始的Markdown内容（与`markdown`相同）。
		- `markdown_with_citations`: 返回网页原始的Markdown内容，并生成带有学术风格的引用链接引用。
		- `references_markdown`: 返回网页中的链接和引用格式的参考文献。
		- `cleared_html`: 经过净化的 HTML 版本(如使用了CSS选择器进行内容选择)
		- `fit_html`: 如果应用了内容过滤 （Pruning/BM25），则返回过滤后的HTML内容，否则为空。
	- 配置文件中的"content_filter_choice"目前只有`Pruning`和`BM25`两种选择，已经配置好了`pruning`，需要`BM25`的话可自行参考官方文档进行配置。
	-   **项目默认的爬虫配置项足够普通人员使用，但如果需要更高级的配置项，可以参考[crawl4ai 官方文档](https://docs.crawl4ai.com/)的文档进行配置。配置文件中的每个键都是顶级键。**

	- 目前默认不支持以下配置项，如有需要可自行修改源码:
		- 高级代理`proxy_config`
		- 设置请求头`headers`
		- 提取结构化数据`extraction_strategy`
		- LLM配置`llm_config`
		- 等其他字典型爬虫配置项

4. **依赖注入**：
	- 使用`dependencies.py`文件加载浏览器配置和爬虫运行配置。

## API 使用方法

### 爬虫路由 `/api/crawl`

- **请求参数**：
	- `url`：要爬取的URL（查询参数形式传入）。

- **响应格式**：
	- 成功时返回`CrawlResponse`对象，包含爬取结果。
	- 错误时返回错误信息。

- **示例请求**：

```bash
curl "http://localhost:8000/api/crawl?url=https://example.com"
```

- **示例响应**：

```json
{
  "seccess": true,
  "content": "爬取的网页内容",
  "error_message": null
}
```

## 依赖项说明

- **fastapi>=0.68.0**：用于构建API的Web框架。
- **uvicorn>=0.15.0**：用于运行FastAPI应用的ASGI服务器。
- **pydantic>=1.8.0**：用于数据验证和设置管理的库。
- **crawl4ai>=0.1.0**：用于网页爬取的核心库。
- **watchdog>=2.1.0**：用于监听配置文件变化的库。
- **validators>=0.18.2**：用于URL验证的库。

## 运行说明

1. 确保已安装Python和pip。
2. 在`backend/`目录下运行以下命令：

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

3. 访问`http://localhost:8000`会显示欢迎消息。
## 注意事项

- 请确保配置文件`config/config.json`存在。