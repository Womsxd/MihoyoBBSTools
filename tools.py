import uuid
import time
import config
import random
import string
import hashlib
import setting


# md5计算
def md5(text: str) -> str:
    md5 = hashlib.md5()
    md5.update(text.encode())
    return md5.hexdigest()


# 随机文本
def random_text(num: int) -> str:
    return ''.join(random.sample(string.ascii_lowercase + string.digits, num))


# 时间戳
def timestamp() -> int:
    return int(time.time())


# 获取请求Header里的DS 当web为true则生成网页端的DS
def get_ds(web: bool, web_old: bool) -> str:
    if web:
        if web_old:
            n = setting.mihoyobbs_Salt_web_old
        else:
            n = setting.mihoyobbs_Salt_web
    else:
        n = setting.mihoyobbs_Salt
    i = str(timestamp())
    r = random_text(6)
    c = md5("salt=" + n + "&t=" + i + "&r=" + r)
    return f"{i},{r},{c}"


# 生成一个device id
def get_device_id() -> str:
    return str(uuid.uuid3(uuid.NAMESPACE_URL, config.config["account"]["cookie"])).replace(
        '-', '').upper()


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
