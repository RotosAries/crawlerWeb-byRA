from .core.config_loader import ConfigLoader
from crawl4ai.async_configs import BrowserConfig, CrawlerRunConfig

def get_browser_config() -> BrowserConfig:
    config_loader = ConfigLoader()
    return config_loader.load_browser_config()

def get_crawler_config() -> CrawlerRunConfig:
    config_loader = ConfigLoader()
    return config_loader.load_crawler_config()
