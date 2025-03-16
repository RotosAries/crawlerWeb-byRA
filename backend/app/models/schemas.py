from pydantic import BaseModel
from typing import Optional, Dict
from crawl4ai.async_configs import BrowserConfig, CrawlerRunConfig

class CrawlRequest(BaseModel):
    model_config = {"arbitrary_types_allowed": True}
    url: str
    browser_config: BrowserConfig
    crawler_run_config: CrawlerRunConfig
    output_format: str

class CrawlResponse(BaseModel):
    success: bool
    content: Optional[str] = None
    error_message: Optional[str] = None