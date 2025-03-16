from pydantic import BaseModel
from typing import Optional, Dict

class CrawlRequest(BaseModel):
    url: str
    browser_config: Dict
    crawler_run_config: Dict

class CrawlResponse(BaseModel):
    success: bool
    content: Optional[str] = None
    error_message: Optional[str] = None