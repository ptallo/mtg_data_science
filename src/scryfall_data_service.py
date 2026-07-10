import json, re
import pandas as pd
from PIL import Image
from src.cache_service import CacheService
from src.scryfall_http_service import ScryfallHttpService

def _card_name_to_cache_key(name: str) -> str:
    return re.sub(r"([,\s\"\-']+)", "_", name).lower()

class ScryfallDataService:
    def __init__(self, base_url: str, json_cache_service: CacheService, png_cache_service: CacheService, http_client: ScryfallHttpService):
        self.json_cache_service = json_cache_service
        self.png_cache_service = png_cache_service
        self.http_client = http_client
        self.base_url = base_url
        self.endpoints = {
            "bulk-data": "bulk-data",
        }

    def get_bulk_data(self) -> pd.DataFrame:
        cache_contents = self.json_cache_service.get(self.endpoints['bulk-data'])
        if cache_contents is not None:
            return pd.DataFrame(json.loads(cache_contents).get("data"))

        response_json = self.http_client.get(f"{self.base_url}/{self.endpoints['bulk-data']}")
        self.json_cache_service.set(self.endpoints['bulk-data'], json.dumps(response_json.json(), indent=4))
        cache_contents = self.json_cache_service.get(self.endpoints['bulk-data'])
        return pd.DataFrame(json.loads(cache_contents).get("data"))

    def get_oracle_cards(self) -> pd.DataFrame:
        cache_key = 'oracle-cards'
        res_df = self.get_bulk_data()
        download_uri = res_df[res_df['name'] == 'Oracle Cards']['download_uri'].iloc[0]

        cache_contents = self.json_cache_service.get(cache_key)
        if cache_contents is not None:
            return pd.DataFrame(json.loads(cache_contents))

        response = self.http_client.get(download_uri, stream=True)
        self.json_cache_service.set(cache_key, response.content)
        cache_contents = self.json_cache_service.get(cache_key) 

        cards_df = pd.DataFrame(json.loads(cache_contents))
        cards_df['image_uri'] = cards_df['image_uris'].apply(lambda x: x.get('normal') if isinstance(x, dict) else None)
        cards_df['price_usd'] = cards_df['prices'].apply(lambda x: x.get('usd') if isinstance(x, dict) else None)
        return cards_df

    def get_default_cards(self) -> pd.DataFrame:
        cache_key = 'default-cards'
        res_df = self.get_bulk_data()
        download_uri = res_df[res_df['name'] == 'Default Cards']['download_uri'].iloc[0]

        cache_contents = self.json_cache_service.get(cache_key)
        if cache_contents is not None:
            return pd.DataFrame(json.loads(cache_contents))

        response = self.http_client.get(download_uri, stream=True)
        self.json_cache_service.set(cache_key, response.content)
        cache_contents = self.json_cache_service.get(cache_key) 
        return pd.DataFrame(json.loads(cache_contents))

    def get_card_images(self, card_names: list[str]) -> dict[str, Image.Image | None]:
        scryfall_df = self.get_oracle_cards()
        scryfall_df = scryfall_df[scryfall_df['name'].isin(card_names)]
        scryfall_df = scryfall_df[['name', 'image_uri']].dropna(subset=['image_uri'])
        scryfall_df['cache_key'] = scryfall_df['name'].apply(_card_name_to_cache_key)

        get_image_bytes = lambda key, image_uri: \
            self.png_cache_service.get(key) \
            if self.png_cache_service.has(key) else \
            self.http_client.get(image_uri, stream=True).content

        scryfall_df['image_bytes'] = scryfall_df.apply(lambda row: get_image_bytes(row['cache_key'], row['image_uri']), axis=1)
        print({k: v for k, v in scryfall_df[['cache_key', 'image_bytes']].to_dict(orient='records').items()})
        pass
