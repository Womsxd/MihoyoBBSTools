'''
Author: Night-stars-1 nujj1042633805@gmail.com
Date: 2023-08-26 12:11:56
LastEditors: Night-stars-1 nujj1042633805@gmail.com
LastEditTime: 2023-08-31 16:20:29
Description: 

Copyright (c) 2023 by Night-stars-1, All Rights Reserved. 
'''
import hashlib
import random
import string
import sys
import time
from pathlib import Path
from typing import Type

from loguru import logger
from pydantic import ValidationError

from .config import ConfigManager
from .data_model import GeetestResult
from .request import post

log = logger

_conf = ConfigManager.data_obj

ROOT_PATH = Path(__name__).parent.absolute()

def set_logger():
    level = "DEBUG"
    log.remove()
    log.add(sys.stdout, level=level, colorize=True,
                format="<cyan>{module}</cyan>.<cyan>{function}</cyan>"
                        ":<cyan>{line}</cyan> - "
                        "<level>{message}</level>")
    path_log = ROOT_PATH / "logs" / "日志文件.log"
    log.add(path_log,
                format="{time:HH:mm:ss} - "
                        "{level}\t| "
                        "{module}.{function}:{line} - "+" {message}",
                rotation="1 days", enqueue=True, serialize=False, encoding="utf-8", retention="10 days")
set_logger()

IncorrectReturn = (KeyError, TypeError, AttributeError, IndexError, ValidationError)
"""米游社API返回数据无效会触发的异常组合"""
def is_incorrect_return(exception: Exception, *addition_exceptions: Type[Exception]) -> bool:
    """
    判断是否是米游社API返回数据无效的异常
    :param exception: 异常对象
    :param addition_exceptions: 额外的异常类型，用于触发判断
    """
    """
        return exception in IncorrectReturn or
            exception.__cause__ in IncorrectReturn or
            isinstance(exception, IncorrectReturn) or
            isinstance(exception.__cause__, IncorrectReturn)
    """
    exceptions = IncorrectReturn + addition_exceptions
    return isinstance(exception, exceptions) or isinstance(exception.__cause__, exceptions)

async def get_validate(gt: str = None, challenge: str = None):
    """
    使用打码平台获取人机验证validate

    :param gt: 验证码gt
    :param challenge: challenge
    """
    content = {
        "gt": gt,
        "challenge": challenge
    }
    
    if gt and challenge and _conf.preference.geetest_url:
        res = await post(
            _conf.preference.geetest_url,
            timeout=60,
            json=content
        )
        geetest_data = res.json()
        if geetest_data['data']['result'] != 'fail':
            return GeetestResult(validate=geetest_data['data']['validate'], seccode="")
    else:
        return GeetestResult("", "")


# TODO 待优化
# md5计算
def md5(text: str) -> str:
    _md5 = hashlib.md5()
    _md5.update(text.encode())
    return _md5.hexdigest()

# 随机文本
def random_text(num: int) -> str:
    return ''.join(random.sample(string.ascii_lowercase + string.digits, num))

# 时间戳
def timestamp() -> int:
    return int(time.time())


# 获取请求Header里的DS 当web为true则生成网页端的DS
def get_ds(web: bool) -> str:
    if web:
        salt = _conf.salt.mihoyobbs_salt_web
    else:
        salt = _conf.salt.mihoyobbs_salt
    t = str(timestamp())
    r = random_text(6)
    c = md5("salt=" + salt + "&t=" + t + "&r=" + r)
    return f"{t},{r},{c}"


# 获取请求Header里的DS(版本2) 这个版本ds之前见到都是查询接口里的
def get_ds2(q: str, b: str) -> str:
    n = _conf.salt.mihoyobbs_salt_x6
    i = str(timestamp())
    r = str(random.randint(100001, 200000))
    add = f'&b={b}&q={q}'
    c = md5("salt=" + n + "&t=" + i + "&r=" + r + add)
    return f"{i},{r},{c}"


# 获取签到的奖励名称
def get_item(raw_data: dict) -> str:
    temp_name = raw_data["name"]
    temp_cnt = raw_data["cnt"]
    return f"{temp_name}x{temp_cnt}"


# 获取明天早晨0点的时间戳
def next_day() -> int:
    now_time = int(time.time())
    next_day_time = now_time - now_time % 86400 + time.timezone + 86400
    return next_day_time


# 获取ua 防止出现多个miHoYoBBS
def get_useragent() -> str:
    if config.config["games"]["cn"]["useragent"] == "":  # 没设置自定义ua就返回默认ua
        return setting.headers['User-Agent']
    if "miHoYoBBS" in config.config["games"]["cn"]["useragent"]:  # 防止出现多个miHoYoBBS
        i = config.config["games"]["cn"]["useragent"].index("miHoYoBBS")
        if config.config["games"]["cn"]["useragent"][i - 1] == " ":
            i = i-1
        return f'{config.config["games"]["cn"]["useragent"][:i]} miHoYoBBS/{setting.mihoyobbs_version}'
    return f'{config.config["games"]["cn"]["useragent"]} miHoYoBBS/{setting.mihoyobbs_version}'


# 获取Openssl版本
def get_openssl_version() -> int:
    try:
        import ssl
    except ImportError:
        from loghelper import log
        log.error("Openssl Lib Error !!")
        # return -99
        # 建议直接更新Python的版本，有特殊情况请提交issues
        exit(-1)
    temp_list = ssl.OPENSSL_VERSION_INFO
    return int(f"{str(temp_list[0])}{str(temp_list[1])}{str(temp_list[2])}")
