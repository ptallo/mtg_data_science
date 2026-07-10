import os
from enum import Enum

from src import file_service

class CacheType(Enum):
    JSON = "json"
    PNG = "png"

class CacheService:
    def __init__(self, cache_dir: str, cache_type: CacheType = CacheType.JSON):
        self.cache_dir = cache_dir
        self.cache_type = cache_type

    def _get_key_fpath(self, key: str) -> str:
        return os.path.join(self.cache_dir, f'{key}.{self.cache_type.value}')

    def has(self, key: str) -> bool:
        return os.path.exists(self._get_key_fpath(key))

    def get(self, key: str) -> str | bytes | None:
        fpath = self._get_key_fpath(key)
        return file_service.read_file(fpath) if os.path.exists(fpath) else None

    def set(self, key: str, value: str | bytes) -> None:
        fpath = self._get_key_fpath(key)
        file_service.write_file(fpath, value)

    def delete(self, key: str) -> None:
        fpath = self._get_key_fpath(key)
        if not os.path.exists(fpath):
            return
        os.remove(fpath)

    def clear(self) -> None:
        if not os.path.exists(self.cache_dir):
            return
        files = [x.split(".")[0] for x in os.listdir(self.cache_dir)]
        for f in files:
            self.delete(f)