import json
import os
from pathlib import Path
from crawl4ai.async_configs import BrowserConfig, CrawlerRunConfig, CacheMode
from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator
from crawl4ai.content_filter_strategy import PruningContentFilter, BM25ContentFilter
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

        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        self._watcher = ConfigWatcher(self.config_path, self._reload_config)
        self._watcher.start()

        self._config_cache = {}

        self.file_isJson_exist = self._validate_config_path()


    def _reload_config(self):
        """清空配置缓存，强制重新加载配置文件。"""
        self._config_cache = {}

    def _validate_config_path(self) -> bool:
        """验证配置文件是否存在，是否为JSON格式。"""
        if not self.config_path.exists():
            print(f"配置文件未找到: {self.config_path}")
            return False
        if self.config_path.suffix.lower() != '.json':
            print("仅支持JSON格式配置文件")
            return False
        return True

    def _validate_file(self) -> bool:
        """验证配置文件内容是否有效。"""
        if not self.file_isJson_exist:
            return False
        
        try:
            with open(self.config_path, 'r') as f:
                if os.stat(self.config_path).st_size == 0:
                    print("配置文件为空")
                    return False
                
                full_config = json.load(f)

                # 当json的根结构不是字典时，给出警告
                if not isinstance(full_config, dict):
                    print("配置文件根结构不是字典类型")
                    return False
        except json.JSONDecodeError as e:
            print(f"配置文件JSON格式错误: {e}")
            return False
        except (FileNotFoundError, PermissionError, IsADirectoryError) as e:
            print(f"无法访问配置文件: {e}")
            return False
        except Exception as e:
            print(f"未知错误: {e}")
            return False
        return True

    def load_output_format(self) -> str:
        """加载并验证输出格式配置。
        
        Returns:
            str: 输出格式，默认为"markdown"。
        """
        print("正在加载输出格式配置...")
        if "output_format" not in self._config_cache:
            if not self.file_isJson_exist or not self._validate_file():
                print("警告: 输出格式加载失败，本次将使用默认的输出格式“markdown”")
                return "markdown"

            config_data = "markdown"
            if not self._is_config_section_exist("output_format"):
                print("警告: “output_format”配置项不存在, 将使用默认输出格式“markdown”")
            elif self._is_config_section_empty("output_format"):
                print("警告: “output_format”配置项为空, 将使用默认输出格式“markdown”")
            else:
                config_data = self._load_config_section("output_format").lower()
                if config_data not in self.VALID_OUTPUT_FORMATS:
                    print(f"警告: “output_format”配置项的值“{config_data}”无效, 将使用默认输出格式“markdown”")
                    config_data = "markdown"
            print(f"输出格式加载成功，当前输出格式为: {config_data}")
            self._config_cache["output_format"] = config_data
        return self._config_cache["output_format"]

    def load_browser_config(self) -> BrowserConfig:
        """加载浏览器配置。
        
        Returns:
            BrowserConfig: 浏览器配置对象。
        """
        print("正在加载浏览器配置...")
        if "browser_config" not in self._config_cache:
            if not self.file_isJson_exist or not self._validate_file():
                print("警告: 浏览器配置加载失败，本次将不会使用此配置")
                return BrowserConfig()

            config_data = {}
            if not self._is_config_section_exist("browser_config"):
                print("警告: “browser_config”配置项不存在, 将不会使用浏览器配置")
            elif self._is_config_section_empty("browser_config"):
                print("警告: “browser_config”配置项为空, 将不会使用浏览器配置")
            else:
                config_data = self._load_config_section("browser_config")
                print("浏览器配置加载成功")
                
            self._config_cache["browser_config"] = BrowserConfig(**config_data) if config_data else BrowserConfig()
        return self._config_cache["browser_config"]

    def load_crawler_config(self) -> CrawlerRunConfig:
        """加载爬虫运行配置。
        
        Returns:
            CrawlerRunConfig: 爬虫运行配置对象。
        """
        print("正在加载爬虫配置...")
        if "crawler_run_config" not in self._config_cache:
            if not self.file_isJson_exist or not self._validate_file():
                print("警告: 爬虫配置加载失败，本次将不会使用此配置")
                return CrawlerRunConfig()
                
            config_data = {}
            if not self._is_config_section_exist("crawler_run_config"):
                print("警告: “crawler_run_config”配置项不存在, 将不会使用爬虫配置")
            elif self._is_config_section_empty("crawler_run_config"):
                print("警告: “crawler_run_config”配置项为空, 将不会使用爬虫配置")
            else:
                config_data = self._load_config_section("crawler_run_config")

                if "cache_mode" in config_data:
                    if config_data["cache_mode"] not in CacheMode.__members__:
                        print(f"警告: “cache_mode”配置项的值“{config_data['cache_mode']}”无效, 将使用默认缓存模式“ENABLED”")
                        config_data["cache_mode"] = CacheMode.ENABLED
                    else : config_data["cache_mode"] = CacheMode[config_data["cache_mode"]]

                if not self._is_config_section_exist("markdown_generator_config"):
                    print("爬虫配置加载成功")
                else:
                    if self._is_config_section_empty("markdown_generator_config"):
                        print("警告: “markdown_generator_config”配置项为空, 将不使用此配置")
                        print("爬虫配置加载成功，但未正确配置Markdown生成器")
                    else:
                        config_data["markdown_generator"] = self.load_md_generator_config()
                        print("爬虫配置加载成功，已正确配置Markdown生成器")
                
            self._config_cache["crawler_run_config"] = CrawlerRunConfig(**config_data) if config_data else CrawlerRunConfig()
        return self._config_cache["crawler_run_config"]

    def load_md_generator_config(self) -> DefaultMarkdownGenerator:
        """加载Markdown生成器配置。
        
        Returns:
            DefaultMarkdownGenerator: Markdown生成器配置对象。
        """
        print("正在加载Markdown生成器配置...")
        if "markdown_generator_config" not in self._config_cache:
            config_data = self._load_config_section("markdown_generator_config")
            if not self._is_config_section_exist("content_filter_choice"):
                print("Markdown生成器配置加载成功")
            else:
                if self._is_config_section_empty("content_filter_choice"):
                    print("警告: “content_filter_choice”配置项为空, 将不使用内容过滤器")
                    print("Markdown生成器配置加载成功，但未选择内容过滤器")
                else:
                    if self._load_config_section("content_filter_choice") not in {"pruning","BM25"}:
                        print(f"警告: “content_filter_choice”配置项的值“{self._load_config_section('content_filter_choice')}”无效, 将不使用内容过滤器")
                        print("Markdown生成器配置加载成功，但未正确选择内容过滤器，目前仅支持pruning和BM25两种内容过滤器")
                    else:
                        if self._load_config_section("content_filter_choice") == "pruning":
                            if not self._is_config_section_exist("pruning_content_filter_config"):
                                print("警告: “pruning_content_filter_config”配置项不存在, 将不使用内容过滤器")
                                print("Markdown生成器配置加载成功，但未配置pruning内容过滤器")
                            elif self._is_config_section_empty("pruning_content_filter_config"):
                                print("警告: “pruning_content_filter_config”配置项为空, 将不使用内容过滤器")
                                print("Markdown生成器配置加载成功，但未正确配置pruning内容过滤器")
                            else:
                                config_data["content_filter"] = self.load_pruning_content_filter_config()
                                print(f"Markdown生成器配置加载成功，已正确配置pruning内容过滤器")
                        else:
                            if not self._is_config_section_exist("BM25_content_filter_config"):
                                print("警告: “BM25_content_filter_config”配置项不存在, 将不使用内容过滤器")
                                print("Markdown生成器配置加载成功，但未配置BM25内容过滤器")
                            elif self._is_config_section_empty("BM25_content_filter_config"):
                                print("警告: “BM25_content_filter_config”配置项为空, 将不使用内容过滤器")
                                print("Markdown生成器配置加载成功，但未正确配置BM25内容过滤器")
                            else:
                                config_data["content_filter"] = self.load_BM25_content_filter_config()
                                print(f"Markdown生成器配置加载成功，已正确配置BM25内容过滤器")

            self._config_cache["markdown_generator_config"] = DefaultMarkdownGenerator(**config_data)
        return self._config_cache["markdown_generator_config"]

    def load_pruning_content_filter_config(self) -> PruningContentFilter:
        """加载pruning内容过滤器配置。
        
        Returns:
            PruningContentFilter: pruning内容过滤器对象。
        """
        print("正在加载pruning内容过滤器配置...")
        if "pruning_content_filter_config" not in self._config_cache:
            config_data = self._load_config_section("pruning_content_filter_config")
            print("pruning内容过滤器配置加载成功")
            self._config_cache["pruning_content_filter_config"] = PruningContentFilter(**config_data)
        return self._config_cache["pruning_content_filter_config"]

    def load_BM25_content_filter_config(self) -> BM25ContentFilter:
        """加载BM25内容过滤器配置。

        Returns:
            BM25ContentFilter: BM25内容过滤器对象。
        """
        print("正在加载BM25内容过滤器配置...")
        if "BM25_content_filter_config" not in self._config_cache:
            config_data = self._load_config_section("BM25_content_filter_config")
            print("BM25内容过滤器配置加载成功")
            self._config_cache["BM25_content_filter_config"] = BM25ContentFilter(**config_data)
        return self._config_cache["BM25_content_filter_config"]


    def _is_config_section_exist(self, section: str) -> bool:
        """检查配置项是否存在。
        
        Args:
            section (str): 配置项名称。
            
        Returns:
            bool: 如果配置项存在，返回True，否则返回False。
        """
        with open(self.config_path, 'r') as f:
            full_config = json.load(f)
            if section not in full_config:
                return False
            return True

    def _is_config_section_empty(self, section: str) -> bool:
        """检查配置项是否为空。
        
        Args:
            section (str): 配置项名称。
            
        Returns:
            bool: 如果配置项为空，返回True，否则返回False。
        """
        with open(self.config_path, 'r') as f:
            full_config = json.load(f)
            if not full_config[section]:
                return True
            return False


    def _load_config_section(self, section: str):
        """加载特定配置项的内容。
        
        Args:
            section (str): 配置项名称。
            
        Returns:
            dict or str: 配置项的内容，如果加载失败则返回默认值default_value。
        """
        default_value = "" if section == "output_format" else {}
        
        try:
            # 处理文件访问异常
            with open(self.config_path, 'r') as f:
                full_config = json.load(f)
                
                # 检查目标section的数据类型
                section_value = full_config.get(section)
                if isinstance(section_value, dict):
                    return section_value
                elif isinstance(section_value, str) or section_value is None:
                    return section_value if section_value is not None else default_value
                else:
                    print(f"警告: “{section}”获取失败，配置项类型无效，应为字典或字符串，将使用默认空值")
                    return default_value
        # 捕获其他未知异常
        except Exception as e:
            print(f"未知错误: {e}")
            return default_value