from urllib.parse import urlparse, urlunparse
import validators

class URLUtils:
    @staticmethod
    def validate_url(url: str) -> bool:
        return validators.url(url)

    @staticmethod
    def validate_protocol(url: str) -> bool:
        parsed_url = urlparse(url)
        return parsed_url.scheme in ('http', 'https')

    @staticmethod
    def clean_url(parsed_url: str) -> str:
        return urlunparse(parsed_url._replace(fragment=""))

    @staticmethod
    def process_url(url: str) -> str:
        if not URLUtils.validate_url(url):
            raise ValueError("Invalid URL format")
        parsed_url = urlparse(url)
        if not URLUtils.validate_protocol(url):
            raise ValueError("Only 'http' and 'https' protocols are supported")
        return URLUtils.clean_url(parsed_url)