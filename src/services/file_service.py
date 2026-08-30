import os

def write_file(fpath: str, content: str | bytes) -> None:
    if not os.path.exists(os.path.dirname(fpath)):
        os.makedirs(os.path.dirname(fpath))

    if isinstance(content, str):
        with open(fpath, "wb") as f:
            f.write(content.encode("utf-8"))
    elif isinstance(content, bytes):
        with open(fpath, "wb") as f:
            f.write(content)
    
def read_file(fpath: str) -> str | bytes:
    with open(fpath, "rb") as f:
        b = f.read()
    return b.decode('utf-8') if fpath.endswith(('.json', '.csv', '.txt')) else b
