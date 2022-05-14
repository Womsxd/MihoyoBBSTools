try:
    # 优先使用httpx，在httpx无法使用的环境下使用requests
    import httpx

    http = httpx.Client(timeout=10, transport=httpx.HTTPTransport(retries=5))
    # 当openssl版本小于1.0.2的时候直接进行一个空请求让httpx报错
    import tools

    if tools.get_openssl_version() <= 102:
        httpx.get()
except (TypeError, ModuleNotFoundError):
    import requests
    from requests.adapters import HTTPAdapter

    http = requests.Session()
    http.mount('http://', HTTPAdapter(max_retries=5))
    http.mount('https://', HTTPAdapter(max_retries=5))
