import json
from pathlib import Path
from crawl4ai.async_configs import BrowserConfig, CrawlerRunConfig, CacheMode
from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator
from crawl4ai.content_filter_strategy import PruningContentFilter
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class ConfigWatcher:
    """监控配置文件变化的类，当配置文件被修改时触发回调函数。"""
    def __init__(self, config_path, callback):
        """初始化ConfigWatcher实例。
        
        Args:
            config_path (str): 配置文件的路径。
            callback (function): 当配置文件被修改时触发的回调函数。
        """
        self.config_path = config_path
        self.callback = callback
        self.observer = Observer()
        self.event_handler = ConfigFileEventHandler(self.config_path, self.callback)

    def start(self):
        """启动文件监控，开始监听配置文件的变化。"""
        self.observer.schedule(self.event_handler, path=str(self.config_path.parent), recursive=False)
        self.observer.start()

    def stop(self):
        """停止文件监控，释放资源。"""
        self.observer.stop()
        self.observer.join()

class ConfigFileEventHandler(FileSystemEventHandler):
    """处理文件系统事件的类，用于监听配置文件的修改事件。"""
    def __init__(self, config_path, callback):
        """初始化ConfigFileEventHandler实例。
        
        Args:
            config_path (str): 配置文件的路径。
            callback (function): 当配置文件被修改时触发的回调函数。
        """
        self.config_path = config_path
        self.callback = callback

    def on_modified(self, event):
        """当配置文件被修改时调用此方法。
        
        Args:
            event (FileSystemEvent): 文件系统事件对象。
        """
        if event.src_path == str(self.config_path):
            self.callback()

class ConfigLoader:
    """加载和验证配置文件的类，支持多种配置项的加载和缓存。"""
    VALID_OUTPUT_FORMATS = {
        "markdown",
        "fit_markdown",
        "raw_markdown",
        "markdown_with_citations",
        "references_markdown",
        "html",
        "cleared_html",
        "fit_html",
    }

    def __init__(self, config_path="./config/config.json"):
        """初始化ConfigLoader实例。
        
        Args:
            config_path (str): 配置文件的路径，默认为"./config/config.json"。
        """
        current_file_path = Path(__file__)
        self.config_path = current_file_path.parent.parent.joinpath(config_path)
        self._validate_config_path()
        self._config_cache = {}
        self._watcher = ConfigWatcher(self.config_path, self._reload_config)
        self._watcher.start()

    def _reload_config(self):
        """清空配置缓存，强制重新加载配置文件。"""
        self._config_cache = {}

    def _validate_config_path(self):
        """验证配置文件路径是否存在且为JSON格式。
        
        Raises:
            FileNotFoundError: 如果配置文件不存在。
            ValueError: 如果配置文件不是JSON格式。
        """
        if not self.config_path.exists():
            # raise FileNotFoundError(f"配置文件未找到: {self.config_path}")
            print(f"配置文件未找到: {self.config_path}")
            return False
        if self.config_path.suffix.lower() != '.json':
            # raise ValueError("仅支持JSON格式配置文件")
            print("仅支持JSON格式配置文件")
            return False
        return True

    def load_output_format(self) -> str:
        """加载并验证输出格式配置。
        
        Returns:
            str: 输出格式，默认为"markdown"。
        """
        if "output_format" not in self._config_cache:
            if not self._validate_config_path():
                return "markdown"

            config_data = "markdown"
            if not self._is_config_section_empty("output_format"):
                config_data = self._load_config_section("output_format").lower()
                if config_data not in self.VALID_OUTPUT_FORMATS:
                    print(f"警告: “output_format”配置项的值“{config_data}”无效, 将使用默认值“markdown”")
                    config_data = "markdown"
                

            self._config_cache["output_format"] = config_data
        return self._config_cache["output_format"]

    def load_browser_config(self) -> BrowserConfig:
        """加载浏览器配置。
        
        Returns:
            BrowserConfig: 浏览器配置对象。
        """
        if "browser_config" not in self._config_cache:
            if not self._validate_config_path():
                return BrowserConfig()

            config_data = {}
            if not self._is_config_section_empty("browser_config"):
                config_data = self._load_config_section("browser_config")
                print("浏览器配置加载成功")
                
            self._config_cache["browser_config"] = BrowserConfig(**config_data) if config_data else BrowserConfig()
        return self._config_cache["browser_config"]

    def load_crawler_config(self) -> CrawlerRunConfig:
        """加载爬虫运行配置。
        
        Returns:
            CrawlerRunConfig: 爬虫运行配置对象。
        """
        if not self._validate_config_path():
            return CrawlerRunConfig()

        if "crawler_run_config" not in self._config_cache:
            config_data = {}
            if not self._is_config_section_empty("crawler_run_config"):
                config_data = self._load_config_section("crawler_run_config")
            
                if "cache_mode" in config_data:
                    config_data["cache_mode"] = CacheMode[config_data["cache_mode"]]

                if not self._is_config_section_empty("markdown_generator_config"):
                    config_data["markdown_generator"] = self.load_md_generator_config()
                print("爬虫配置加载成功")

            self._config_cache["crawler_run_config"] = CrawlerRunConfig(**config_data) if config_data else CrawlerRunConfig()
        return self._config_cache["crawler_run_config"]

    def load_md_generator_config(self) -> DefaultMarkdownGenerator:
        """加载Markdown生成器配置。
        
        Returns:
            DefaultMarkdownGenerator: Markdown生成器配置对象。
        """
        if "markdown_generator_config" not in self._config_cache:
            config_data = self._load_config_section("markdown_generator_config")
            print("Markdown生成器配置加载成功")

            if not self._is_config_section_empty("puning_content_filter_config"):
                config_data["content_filter"] = self.load_content_filter_config()

            self._config_cache["markdown_generator_config"] = DefaultMarkdownGenerator(**config_data)
        return self._config_cache["markdown_generator_config"]

    def load_content_filter_config(self) -> PruningContentFilter:
        """加载内容过滤器配置。
        
        Returns:
            PruningContentFilter: 内容过滤器配置对象。
        """
        if "puning_content_filter_config" not in self._config_cache:
            config_data = self._load_config_section("puning_content_filter_config")
            print("内容过滤器配置加载成功")
            self._config_cache["puning_content_filter_config"] = PruningContentFilter(**config_data)
        return self._config_cache["puning_content_filter_config"]
    
    def _is_config_section_empty(self, section: str) -> bool:
        """检查配置项是否为空。
        
        Args:
            section (str): 配置项名称。
            
        Returns:
            bool: 如果配置项为空，返回True，否则返回False。
        """
        config_data = self._load_config_section(section)
        return not config_data

    def _load_config_section(self, section: str):
        """加载特定配置项的内容。
        
        Args:
            section (str): 配置项名称。
            
        Returns:
            dict or str: 配置项的内容，如果加载失败则返回默认值。
        """
        default_value = "" if section == "output_format" else {}
        
        try:
            # 处理文件访问异常
            with open(self.config_path, 'r') as f:
                full_config = json.load(f)
                
                # 确保JSON根结构是字典
                if not isinstance(full_config, dict):
                    raise ValueError("配置文件根结构必须是字典类型")
                
                # 检查目标section的数据类型
                section_value = full_config.get(section)
                if isinstance(section_value, dict):
                    return section_value
                elif isinstance(section_value, str) or section_value is None:
                    return section_value if section_value is not None else default_value
                else:
                    print(f"警告: “{section}”配置项类型无效，应为字典或字符串")
                    return default_value
    
        # 处理JSON语法错误
        except json.JSONDecodeError as e:
            print(f"警告: {section}配置文件JSON格式错误: {e}")
            return default_value
    
        # 处理文件路径、权限等问题
        except (FileNotFoundError, PermissionError, IsADirectoryError) as e:
            print(f"警告: 无法访问配置文件: {e}")
            return default_value
    
        # 处理非字典根结构异常
        except ValueError as e:
            print(f"警告: {e}")
            return default_value
    
        # 捕获其他未知异常
        except Exception as e:
            print(f"未知错误: {e}")
            return default_value