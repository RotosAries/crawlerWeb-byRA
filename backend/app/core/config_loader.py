import json
from enum import Enum
from pathlib import Path
from crawl4ai.async_configs import BrowserConfig, CrawlerRunConfig

class ConfigLoader:
    def __init__(self, config_path="../config/config.json"):
        self.config_path = Path(config_path)
        self._validate_config_path()

    def _validate_config_path(self):
        if not self.config_path.exists():
            raise FileNotFoundError(f"配置文件未找到: {self.config_path}")
        if self.config_path.suffix.lower() != '.json':
            raise ValueError("仅支持JSON格式配置文件")

    def load_browser_config(self) -> BrowserConfig:
        config_data = self._load_config_section("browser_config")
        return BrowserConfig(**config_data)

    def load_crawler_config(self) -> CrawlerRunConfig:
        config_data = self._load_config_section("crawler_run_config")
        return CrawlerRunConfig(**config_data)

    def _load_config_section(self, section: str):
        try:
            with open(self.config_path, 'r') as f:
                full_config = json.load(f)
                return full_config.get(section, {})
        except json.JSONDecodeError as e:
            raise ValueError(f"配置文件格式错误: {e}") from e