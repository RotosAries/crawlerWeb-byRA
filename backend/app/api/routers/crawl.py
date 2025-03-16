from fastapi import APIRouter, Depends, HTTPException
from crawl4ai.async_configs import BrowserConfig, CrawlerRunConfig
from ...core.crawler import main as crawl_main
from ...dependencies import get_browser_config, get_crawler_config, get_output_format
from ...models.schemas import CrawlResponse, CrawlRequest
from ...utils.url_utils import URLUtils


router = APIRouter()

@router.get("/crawl", response_model=CrawlResponse)
async def crawl(
    url: str, # 仅支持以查询参数的形式传入url
    browser_config: BrowserConfig = Depends(get_browser_config), # 后端加载浏览器配置，前端无需传入
    crawler_run_config: CrawlerRunConfig = Depends(get_crawler_config), # 后端加载爬虫运行配置，前端无需传入
    output_format: str = Depends(get_output_format) # 后端加载输出格式配置，前端无需传入
    ):

    try:
        # 验证并处理URL
        processed_url = URLUtils.process_url(url)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # 创建爬虫请求对象
    request = CrawlRequest(url=processed_url, browser_config=browser_config, crawler_run_config=crawler_run_config, output_format=output_format)
    try:
        # 调用爬虫主函数
        response = await crawl_main(request)
        return response
    except Exception as e:
        # 处理异常并返回错误信息
        raise HTTPException(status_code=500, detail=str(e))
