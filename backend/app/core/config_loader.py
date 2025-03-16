import json
from pathlib import Path
from crawl4ai.async_configs import BrowserConfig, CrawlerRunConfig, CacheMode
from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator
from crawl4ai.content_filter_strategy import PruningContentFilter
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class ConfigWatcher:
    def __init__(self, config_path, callback):
        self.config_path = config_path
        self.callback = callback
        self.observer = Observer()
        self.event_handler = ConfigFileEventHandler(self.config_path, self.callback)

    def start(self):
        self.observer.schedule(self.event_handler, path=str(self.config_path.parent), recursive=False)
        self.observer.start()

    def stop(self):
        self.observer.stop()
        self.observer.join()

class ConfigFileEventHandler(FileSystemEventHandler):
    def __init__(self, config_path, callback):
        self.config_path = config_path
        self.callback = callback

    def on_modified(self, event):
        if event.src_path == str(self.config_path):
            self.callback()

class ConfigLoader:
    def __init__(self, config_path="./config/config.json"):
        current_file_path = Path(__file__)
        self.config_path = current_file_path.parent.parent.joinpath(config_path)
        self._validate_config_path()
        self._config_cache = {}
        self._watcher = ConfigWatcher(self.config_path, self._reload_config)
        self._watcher.start()

    def _reload_config(self):
        self._config_cache = {}

    def _validate_config_path(self):
        if not self.config_path.exists():
            raise FileNotFoundError(f"配置文件未找到: {self.config_path}")
        if self.config_path.suffix.lower() != '.json':
            raise ValueError("仅支持JSON格式配置文件")

    def load_browser_config(self) -> BrowserConfig:
        if "browser_config" not in self._config_cache:
            config_data = {}
            if not self._is_config_section_empty("browser_config"):
                config_data = self._load_config_section("browser_config")
                
            self._config_cache["browser_config"] = BrowserConfig(**config_data) if config_data else BrowserConfig()
        return self._config_cache["browser_config"]

    def load_crawler_config(self) -> CrawlerRunConfig:
        if "crawler_run_config" not in self._config_cache:
            config_data = {}
            if not self._is_config_section_empty("crawler_run_config"):
                config_data = self._load_config_section("crawler_run_config")
            
                if "cache_mode" in config_data:
                    config_data["cache_mode"] = CacheMode[config_data["cache_mode"]]

                if not self._is_config_section_empty("markdown_generator_config"):
                    config_data["markdown_generator"] = self.load_md_generator_config()

            self._config_cache["crawler_run_config"] = CrawlerRunConfig(**config_data) if config_data else CrawlerRunConfig()
        return self._config_cache["crawler_run_config"]

    def load_md_generator_config(self) -> DefaultMarkdownGenerator:
        if "markdown_generator_config" not in self._config_cache:
            config_data = self._load_config_section("markdown_generator_config")

            if not self._is_config_section_empty("puning_content_filter_config"):
                config_data["content_filter"] = self.load_content_filter_config()

            self._config_cache["markdown_generator_config"] = DefaultMarkdownGenerator(**config_data)
        return self._config_cache["markdown_generator_config"]

    def load_content_filter_config(self) -> PruningContentFilter:
        if "puning_content_filter_config" not in self._config_cache:
            config_data = self._load_config_section("puning_content_filter_config")
            self._config_cache["puning_content_filter_config"] = PruningContentFilter(**config_data)
        return self._config_cache["puning_content_filter_config"]

    def _load_config_section(self, section: str):
        try:
            with open(self.config_path, 'r') as f:
                full_config = json.load(f)
                return full_config.get(section, {})
        except json.JSONDecodeError as e:
            print(f"警告: “{section}”配置文件格式错误: {e}")
            return {}
    
    def _is_config_section_empty(self, section: str) -> bool:
        config_data = self._load_config_section(section)
        return not config_data