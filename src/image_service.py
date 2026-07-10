import re, io
import tkinter as tk
from matplotlib import pyplot as plt
from src.cache_service import CacheService
from src.scryfall_http_service import ScryfallHttpService
from PIL import Image


class ImageService:
    def __init__(self, cache_service: CacheService, http_service: ScryfallHttpService):
        self.cache_service = cache_service
        self.http_service = http_service

    def get_card_images(self, key_to_uri_dict: dict[str, str]) -> dict[str, Image.Image | None]:
        images = {}
        for name, image_uri in key_to_uri_dict.items():
            cache_key = _card_name_to_cache_key(name)
            if self.cache_service.get(cache_key) is not None:
                continue
            response = self.http_service.get(image_uri, stream=True)
            self.cache_service.set(cache_key, response.content)

    def get_pil_image_from_cache(self, name: str) -> Image.Image | None:
        cache_key = _card_name_to_cache_key(name)
        img_bytes = self.cache_service.get(cache_key)
        return Image.open(io.BytesIO(img_bytes)) if img_bytes is not None else None

    def get_images_from_cache(self, names: list[str]) -> list[Image.Image | None]:
        images = [self.get_pil_image_from_cache(n) for n in names]
        return [img for img in images if img is not None]

    def save_images_as_grid(self, images: list[Image.Image | None], columns: int, output_path: str) -> None:
        image_dimensions = (488, 680)
        dpi = tk.Tk().winfo_fpixels('1i')  # Get the screen DPI
        rows = (len(images) + columns - 1) // columns

        fig, axes = plt.subplots(rows, columns, figsize=(columns*image_dimensions[0]/dpi, rows*image_dimensions[1]/dpi), dpi=dpi)
        axes = axes.flatten()

        for ax, img in zip(axes, images):
            ax.imshow(img)
            ax.axis('off')

        plt.tight_layout(h_pad=1, w_pad=1)
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()