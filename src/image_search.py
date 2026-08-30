from src.services.container import Container


if __name__ == "__main__":
    c = Container.get_singleton()
    c.get_service('scryfall_data').download_all_data()