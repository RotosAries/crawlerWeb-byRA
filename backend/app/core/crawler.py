import asyncio
from crawl4ai import AsyncWebCrawler
from crawl4ai.async_configs import BrowserConfig, CrawlerRunConfig, CacheMode
from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator
from crawl4ai.content_filter_strategy import PruningContentFilter

async def main():
    # 配置浏览器运行参数
    browser_config = BrowserConfig(
        headless=True, #无头模式
        verbose=True, #输出详细信息
        text_mode=True #以文本模式爬取页面内容
    )

    # 配置内容过滤器
    content_filter = PruningContentFilter(
        threshold=0.85,
        threshold_type="dynamic",  # or "fixed"
        # min_word_threshold=10  # 最少词数
    )

    # 配置Markdown生成器
    md_generator = DefaultMarkdownGenerator(
        content_filter=content_filter,  # 指定内容过滤器
        options={
            "ignore_links": True,  # 输出不显示超链接
            "ignore_images": True,  # 输出不显示图片
            "escape_html": True,  # 转义HTML标签
        }
    )
    
    # 配置爬虫运行参数
    run_config = CrawlerRunConfig(
        only_text=True, #只爬取文本内容
        cache_mode=CacheMode.ENABLE, #启用缓存
        check_robots_txt=True, #检查robots.txt
        exclude_external_links=True, #不爬取外部链接
        excluded_tags=["script", "style","form","header","footer"], #不爬取script,style,form,header,footer标签内容
        remove_overlay_elements=True,  # 移除弹窗/模态框
        process_iframes=False,      # 不处理iframe内容
        verbose=True, #输出详细信息
        stream=True, #输出为流式数据

        markdown_generator=md_generator, #指定Markdown生成器
    )
    
    # 创建爬虫实例并运行
    async with AsyncWebCrawler(config=browser_config) as crawler:
        result = await crawler.arun(url="https://example.com", config=run_config)
        
        # 检查爬取是否成功并输出结果
        if result.success:
            print("爬取成功！")
            print("过滤后Markdown内容：\n", result.markdown.fit_markdown)
        else:
            print(f"爬取失败：{result.error_message}")

if __name__ == "__main__":
    asyncio.run(main())
