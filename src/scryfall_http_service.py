import requests

class ScryfallHttpService:
    def __init__(self):
        self.project_name = "MTG-DataScience-Project"

    def _get_scryfall_headers(self) -> dict[str, str]:
        return {
            "User-Agent": f"{self.project_name}/1.0",
            "Accept": "application/json;q=0.9,*/*,q=0.8",
        }
    
    def get(self, url: str, **kwargs) -> requests.Response:
        response = requests.get(url, headers=self._get_scryfall_headers(), **kwargs)
        if response.status_code != 200:
            response.raise_for_status()
        return response