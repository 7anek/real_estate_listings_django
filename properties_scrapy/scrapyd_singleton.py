from scrapyd_api import ScrapydAPI


class ScrapydAPISingleton:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = ScrapydAPI(*args, **kwargs)
        return cls._instance
