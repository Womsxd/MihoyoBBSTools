import tools
import request
from typing import Dict
from loghelper import log


def http_get(url: str, max_retries: int = 2, **kwargs):
    return http_request("get", url, max_retries, **kwargs)


def http_get_json(url: str, max_retries: int = 2, **kwargs) -> Dict[str, any]:
    resp = http_get(url, max_retries, **kwargs)
    return resp.json()


def http_post(url: str, max_retries: int = 2, **kwargs):
    return http_request("post", url, max_retries, **kwargs)


def http_post_json(url: str, max_retries: int = 2, **kwargs) -> Dict[str, any]:
    resp = http_post(url, max_retries, **kwargs)
    return resp.json()


def http_request(
        method: str,
        url: str,
        max_retries: int = 2,
        **kwargs
):
    for i in range(max_retries + 1):
        try:
            log.debug(f"{method.upper()} {url}, REQ: {i + 1}/{max_retries}")
            session = request.get_new_session()
            session.headers["USER_AGENT"] = tools.get_useragent()
            resp = session.request(method, url, **kwargs)
            log.debug(f"Response: {resp.status_code}\n\n{resp.text}\n")
        except KeyError as e:
            log.error(f"Wrong response: {e}, REQ: {i + 1}/{max_retries}")
        except Exception as e:
            log.error(f"HTTP /Unknown error: {e}, REQ: {i + 1}/{max_retries}")
        else:
            return resp
    raise Exception(f"所有HTTP请求失败,请检查网络")
