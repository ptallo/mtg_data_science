from typing import Self
from src.services.cache_service import CacheService, CacheType
from src.services.scryfall_http_service import ScryfallHttpService
from src.services.scryfall_data_service import ScryfallDataService

SCRYFALL_BASE_URL = "https://api.scryfall.com/"

class Container:
    def __init__(self):
        self.services = {}

    def register_service(self, name: str, service: any):
        self.services[name] = service

    def get_service(self, name: str) -> any:
        return self.services.get(name)

    @staticmethod
    def get_singleton() -> Self:
        if not hasattr(Container, "_instance"):
            Container._instance = create_container(SCRYFALL_BASE_URL)
        return Container._instance

def create_container(base_url: str) -> Container:
    c = Container()
    c.register_service('json_cache', CacheService("./cache/json/", cache_type=CacheType.JSON))
    c.register_service('png_cache', CacheService("./cache/png/", cache_type=CacheType.PNG))
    c.register_service('scryfall_http', ScryfallHttpService())
    c.register_service('scryfall_data', ScryfallDataService(
        base_url=base_url, 
        json_cache_service=c.get_service('json_cache'),
        png_cache_service=c.get_service('png_cache'),
        http_client=c.get_service('scryfall_http'),
    ))
    return c