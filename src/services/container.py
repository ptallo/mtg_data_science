from typing import Self
from services.cache_service import CacheService, CacheType
from services.scryfall_http_service import ScryfallHttpService
from services.scryfall_data_service import ScryfallDataService

class Container:
    def __init__(self, scryfall_base_url: str):
        self.base_url: str = scryfall_base_url 
        self.json_cache_service = CacheService("./cache/json/", cache_type=CacheType.JSON)
        self.png_cache_service = CacheService("./cache/png/", cache_type=CacheType.PNG)
        self.scryfall_http_service = ScryfallHttpService()
        self.scryfall_data_service = ScryfallDataService(
            base_url=self.base_url, 
            json_cache_service=self.json_cache_service,
            png_cache_service=self.png_cache_service,
            http_client=self.scryfall_http_service,
        )

    @staticmethod
    def get_singleton() -> Self:
        if not hasattr(Container, "_instance"):
            Container._instance = Container(scryfall_base_url="https://api.scryfall.com")
        return Container._instance

    def get_json_cache_service(self) -> CacheService:
        return self.json_cache_service

    def get_png_cache_service(self) -> CacheService:
        return self.png_cache_service

    def get_scryfall_data_service(self) -> ScryfallDataService:
        return self.scryfall_data_service

