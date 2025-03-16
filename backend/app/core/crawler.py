import asyncio
from crawl4ai import AsyncWebCrawler
from config_loader import ConfigLoader

async def main():
    # 加载配置
    loader = ConfigLoader()
    browser_config = loader.load_browser_config()
    run_config = loader.load_crawler_config()

    # 爬虫主逻辑
    async with AsyncWebCrawler(config=browser_config) as crawler:
        result = await crawler.arun(url="https://docs.crawl4ai.com/core/browser-crawler-config/", config=run_config)

    # 检查爬取是否成功并输出结果
    if result.success:
        print("爬取成功！")
        print("原始Markdown内容：\n", result.markdown.raw_markdown)
        print("-------------------------------------------------------------")
        print("过滤后的Markdown内容：\n",result.markdown.fit_markdown)
    else:
        print(f"爬取失败：{result.error_message}")

if __name__ == "__main__":
    asyncio.run(main())