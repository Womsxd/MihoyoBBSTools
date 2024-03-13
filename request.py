import sys


def get_new_session(**kwargs):
    try:
        # 优先使用httpx，在httpx无法使用的环境下使用requests
        import httpx

        http_client = httpx.Client(timeout=20, transport=httpx.HTTPTransport(retries=10), follow_redirects=True,
                                   **kwargs)
        # 当openssl版本小于1.0.2的时候直接进行一个空请求让httpx报错
        import tools

        if tools.get_openssl_version() < 102:
            httpx.get()
    except (TypeError, ModuleNotFoundError) as e:
        import requests
        from requests.adapters import HTTPAdapter

        http_client = requests.Session()
        http_client.mount('http://', HTTPAdapter(max_retries=10))
        http_client.mount('https://', HTTPAdapter(max_retries=10))
    return http_client


def is_module_imported(module_name):
    return module_name in sys.modules


def get_new_session_use_proxy(http_proxy: str):
    if is_module_imported("httpx"):
        proxies = {
            "http://": f'http://{http_proxy}',
            "https://": f'http://{http_proxy}'
        }
        return get_new_session(proxies=proxies)
        # httpx 版本大于0.26.0可用
        # return get_new_session(proxy=f'http://{http_proxy}')
    else:
        session = get_new_session()
        session.proxies = {
            "http": f'http://{http_proxy}',
            "https": f'http://{http_proxy}'
        }
        return session


http = get_new_session()
