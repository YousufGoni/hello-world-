import hashlib
import time


def build_headers(api_key: str, secret: str) -> dict[str, str]:
    timestamp = str(int(time.time()))
    signature = hashlib.sha256((api_key + secret + timestamp).encode("utf-8")).hexdigest()
    return {
        "Api-key": api_key,
        "X-Signature": signature,
        "Accept": "application/json",
        "Accept-Encoding": "gzip",
        "Content-Type": "application/json",
    }
