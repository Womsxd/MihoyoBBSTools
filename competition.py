import re
import time
import random

import config
import account
import setting
from error import CookieError
from loghelper import log
from request import get_new_session


def cookie_get_hk4e_token(cookies: str) -> str:
    """
    从 cookie 中获取 hk4e_token
    :return: hk4e_token
    """
    match = re.search(r"e_hk4e_token=([^;]+)", cookies)
    if match:
        e_hk4e_token = match.group(1)
        return e_hk4e_token
    else:
        return ''


def run_task():
    result = ''
    return result
