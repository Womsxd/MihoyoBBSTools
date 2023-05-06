import json
import logging
import tools
from typing import Dict

import requests
from requests import HTTPError, Response


def http_get(url: str, max_retries: int = 2, **kwargs) -> Response:
    return http_request("get", url, max_retries, **kwargs)


def http_get_json(url: str, max_retries: int = 2, **kwargs) -> Dict[str, any]:
    resp = http_get(url, max_retries, **kwargs)
    data = resp.text
    return json.loads(data)


def http_post(url: str, max_retries: int = 2, **kwargs) -> Response:
    return http_request("post", url, max_retries, **kwargs)


def http_post_json(url: str, max_retries: int = 2, **kwargs) -> Dict[str, any]:
    resp = http_post(url, max_retries, **kwargs)
    data = resp.text
    return json.loads(data)


def http_request(
    method: str,
    url: str,
    max_retries: int = 2,
    **kwargs
) -> Response:
    for i in range(max_retries + 1):
        try:
            logging.debug(f"{method.upper()} {url}, REQ: {i+1}/{max_retries}")
            session = requests.Session()
            session.headers["USER_AGENT"] = tools.get_useragent()
            resp = session.request(method, url, **kwargs)
            logging.debug(f"Response: {resp.status_code}\n\n{resp.text}\n")
        except HTTPError as e:
            logging.error(f"HTTP error: {e}, REQ: {i+1}/{max_retries}")
        except KeyError as e:
            logging.error(f"Wrong response: {e}, REQ: {i+1}/{max_retries}")
        except Exception as e:
            logging.error(f"Unknown error: {e}, REQ: {i+1}/{max_retries}")
        else:
            return resp
    raise Exception(f"所有HTTP请求失败,请检查网络")
