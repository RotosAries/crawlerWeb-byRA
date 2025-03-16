import asyncio
from crawl4ai import AsyncWebCrawler
from ..models.schemas import CrawlRequest, CrawlResponse


async def main(request: CrawlRequest) -> CrawlResponse:

    # 爬虫主逻辑
    async with AsyncWebCrawler(config=request.browser_config) as crawler:
        result = await crawler.arun(url=request.url, config=request.crawler_run_config)

    # 检查爬取是否成功并返回爬取结果
    if result.success:
        return CrawlResponse(success=True, content=result.markdown.fit_markdown)
    else:
        return CrawlResponse(success=False, error_message=result.error_message)