import json, re, io
import pandas as pd
from enum import Enum
from PIL import Image
from src.cache_service import CacheService
from src.scryfall_http_service import ScryfallHttpService

def _card_name_to_cache_key(name: str) -> str:
    return re.sub(r"([,\s\"\-']+)", "_", name).lower()

def _bytes_to_image(b: bytes) -> Image.Image | None:
    return Image.open(io.BytesIO(b)) if not pd.isna(b) else None

class BulkDataType(Enum):
    ORACLE_CARDS = "oracle_cards"
    UNIQUE_ARTWORK = "unqiue_artwork"
    DEFAULT_CARDS = "default_cards"
    ALL_CARDS = "all_cards"
    RULINGS = "rulings"
    ART_TAGS = "art_tags"
    ORACLE_TAGS = "oracle_tags"

class ScryfallDataService:
    def __init__(self, base_url: str, json_cache_service: CacheService, png_cache_service: CacheService, http_client: ScryfallHttpService):
        self.json_cache_service = json_cache_service
        self.png_cache_service = png_cache_service
        self.http_client = http_client
        self.base_url = base_url
        self.endpoints = { "bulk-data": "bulk-data" }
        self.column_sets = {
            'gameplay_columns': [
                'id', 'oracle_id',  'name',  'cmc', 'mana_cost', 'color_identity', 'colors', 'type_line', 'oracle_text', 'power', 
                'toughness', 'keywords', 'game_changer', 'defense', 'hand_modifier', 'life_modifier', 'loyalty', 'produced_mana', 
                'reserved', 'commander_legality', 'price_usd', 'penny_rank', 'edhrec_rank'
            ],
        }

    def clear_caches(self):
        self.json_cache_service.clear()
        self.png_cache_service.clear()

    def _wrap_cache_contents(self, contents: str, json_key: str = None) -> pd.DataFrame:
        df = pd.DataFrame(json.loads(contents) if json_key is None else json.loads(contents).get(json_key))
        if 'image_uris' in df.columns:
            df['image_uri'] = df['image_uris'].apply(lambda x: x.get('normal') if isinstance(x, dict) else None)
        if 'prices' in df.columns:
            df['price_usd'] = df['prices'].apply(lambda x: x.get('usd') if isinstance(x, dict) else None)
        if 'legalities' in df.columns:
            df['commander_legality'] = df['legalities'].apply(lambda x: x.get('commander') if isinstance(x, dict) else None)
        return df

    def _get_bulk_data_download_link(self, bd: BulkDataType) -> str:
        df = self.get_bulk_data().copy()
        return df[df['type'].eq(bd.value)].download_uri.iloc[0]

    def get_bulk_data(self) -> pd.DataFrame:
        if self.json_cache_service.get(self.endpoints['bulk-data']) is not None:
            return self._wrap_cache_contents(self.json_cache_service.get(self.endpoints['bulk-data']), json_key="data")

        response_json = self.http_client.get(f"{self.base_url}/{self.endpoints['bulk-data']}")
        self.json_cache_service.set(self.endpoints['bulk-data'], json.dumps(response_json.json(), indent=4))
        cache_contents = self.json_cache_service.get(self.endpoints['bulk-data'])
        return pd.DataFrame(json.loads(cache_contents).get("data"))

    def get_cards_from_bulk_data(self, col_set_name: str, bd: BulkDataType = BulkDataType.ORACLE_CARDS) -> pd.DataFrame:
        if self.json_cache_service.get(bd.value) is None:
            response = self.http_client.get(self._get_bulk_data_download_link(bd), stream=True)
            self.json_cache_service.set(bd.value, response.content)
        tdf = self._wrap_cache_contents(self.json_cache_service.get(bd.value))
        return tdf if not self.column_sets.get(col_set_name) else tdf[self.column_sets.get(col_set_name)]

    def get_card_images(self, oracle_ids: list[str], bd: BulkDataType = BulkDataType.ORACLE_CARDS) -> dict[str, Image.Image | None]:
        scryfall_df = self.get_cards_from_bulk_data(bd)
        scryfall_df = scryfall_df[scryfall_df['oracle_id'].isin(oracle_ids)].copy()
        scryfall_df = scryfall_df[['oracle_id', 'image_uri']].dropna(subset=['image_uri'])

        if scryfall_df.shape[0] == 0:
            return {}

        get_image_bytes = lambda key, image_uri: \
            self.png_cache_service.get(key) \
            if self.png_cache_service.has(key) else \
            self.http_client.get(image_uri, stream=True).content

        scryfall_df['image_bytes'] = scryfall_df.apply(lambda row: get_image_bytes(row['oracle_id'], row['image_uri']), axis=1)
        scryfall_df.apply(lambda r: self.png_cache_service.set(r['oracle_id'], r['image_bytes']), axis=1)
        temp_dict = scryfall_df[['oracle_id', 'image_bytes']].to_dict(orient="list")
        id_arr, img_arr = temp_dict.get("oracle_id"), temp_dict.get("image_bytes")
        img_arr = [_bytes_to_image(b) for b in img_arr]
        return {k: v for k, v in zip(id_arr, img_arr)}