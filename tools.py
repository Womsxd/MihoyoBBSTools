import hashlib
import random
import string
import sys
import time
import uuid

import setting


def md5(text: str) -> str:
    """
    计算输入文本的 MD5 哈希值。

    :param text: 输入的文本字符串。
    :return: 输入文本的 MD5 哈希值，以十六进制字符串表示。
    """
    _md5 = hashlib.md5()
    _md5.update(text.encode())
    return _md5.hexdigest()


# 随机文本
def random_text(num: int) -> str:
    """
    生成指定长度的随机文本。

    :param num: 随机文本的长度。
    :return: 生成的随机文本。
    """
    return ''.join(random.sample(string.ascii_lowercase + string.digits, num))


def timestamp() -> int:
    """
    获取当前时间戳。

    :return: 当前时间戳。
    """
    return int(time.time())


def get_ds(web: bool) -> str:
    """
    获取米游社的签名字符串，用于访问米游社API时的签名验证。

    :param web: 是否为网页端请求。如果为 True，则使用手机网页端的 salt；如果为 False，则使用移动端的 salt。
    :return: 返回一个字符串，格式为"时间戳,随机字符串,签名"。
    """
    n = setting.mihoyobbs_salt
    if web:
        n = setting.mihoyobbs_salt_web
    i = str(timestamp())
    r = random_text(6)
    c = md5(f'salt={n}&t={i}&r={r}')
    return f"{i},{r},{c}"


def get_ds2(query: str = "", body: str = "") -> str:
    """
    获取米游社的签名字符串，用于访问米游社API时的签名验证。

    :param query: 请求的查询参数
    :param body: 请求的主体内容
    :return: 返回一个字符串，格式为"时间戳,随机字符串,签名"。
    """
    n = setting.mihoyobbs_salt_x6
    i = str(timestamp())
    r = str(random.randint(100001, 200000))
    c = md5(f'salt={n}&t={i}&r={r}&b={body}&q={query}')
    return f"{i},{r},{c}"


def get_device_id(cookie: str) -> str:
    """
    使用 cookie 通过 uuid v3 生成设备 ID。
    :param cookie: cookie

    :return: 设备 ID。
    """
    return str(uuid.uuid3(uuid.NAMESPACE_URL, cookie))


def get_item(raw_data: dict) -> str:
    """
    获取签到的奖励信息

    :param raw_data: 签到的奖励数据
    :return: 签奖励名称x数量
    """
    temp_name = raw_data["name"]
    temp_cnt = raw_data["cnt"]
    return f"{temp_name}x{temp_cnt}"


def get_next_day_timestamp() -> int:
    """
    获取明天凌晨的时间戳。

    :return: 明天凌晨的时间戳
    """
    now_time = int(time.time())
    next_day_time = now_time - now_time % 86400 + time.timezone + 86400
    return next_day_time


def time_conversion(minute: int) -> str:
    """
    将分钟转换为小时和分钟
    :param minute: 分钟
    :return: 小时和分钟
    """
    h = minute // 60
    s = minute % 60
    return f"{h}小时{s}分钟"


def tidy_cookie(cookies: str) -> str:
    """
    整理cookie
    :param cookies: cookie
    :return: 整理后的cookie
    """
    cookie_dict = {}
    for cookie in cookies.split(";"):
        cookie = cookie.strip()
        if cookie == "":
            continue
        key, value = cookie.split("=", 1)
        cookie_dict[key] = value
    return "; ".join([f"{key}={value}" for key, value in cookie_dict.items()])


# 获取ua 防止出现多个miHoYoBBS
def get_useragent(useragent: str) -> str:
    if useragent == "":  # 没设置自定义ua就返回默认ua
        return setting.headers['User-Agent']
    if "miHoYoBBS" in useragent:  # 防止出现多个miHoYoBBS
        i = useragent.index("miHoYoBBS")
        if useragent[i - 1] == " ":
            i = i - 1
        return f'{useragent[:i]} miHoYoBBS/{setting.mihoyobbs_version}'
    return f'{useragent} miHoYoBBS/{setting.mihoyobbs_version}'


def get_openssl_version() -> int:
    """
    获取openssl版本号
    :return: OpenSSL 的版本号。
    """
    try:
        import ssl
    except ImportError:
        sys.exit("Openssl Lib Error !!")
        # return -99
        # 建议直接更新Python的版本，有特殊情况请提交issues
    temp_list = ssl.OPENSSL_VERSION_INFO
    return int(f"{str(temp_list[0])}{str(temp_list[1])}{str(temp_list[2])}")
