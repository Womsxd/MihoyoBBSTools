import re
from copy import deepcopy

import config
import setting
from error import CookieError, StokenError
from loghelper import log
from request import http

headers = setting.headers.copy()
headers.pop("DS")
headers.pop("Origin")
headers.pop("Referer")


def login():
    if not config.config["account"]["cookie"]:
        log.error("请填入 Cookies！")
        config.clear_cookie()
        raise CookieError('No cookie')
    if config.config['account']['stoken'] == "":
        log.error("无 Stoken 请手动填入 stoken！")
        raise StokenError('no stoken')
    uid = get_uid()
    if uid is None:
        log.error("cookie 缺少 UID，请重新抓取 bbs 的 cookie")
        config.clear_cookie()
        raise CookieError('Cookie expires')
    config.config["account"]["stuid"] = uid
    if require_mid():
        config.config["account"]["mid"] = get_mid()
    log.info("登录成功！")
    log.info("正在保存 Config！")
    config.save_config()


def get_login_ticket() -> str:
    ticket_match = re.search(r'login_ticket=(.*?)(?:;|$)', config.config["account"]["cookie"])
    return ticket_match.group(1) if ticket_match else None


def get_mid() -> str:
    mid = re.search(r'(account_mid_v2|ltmid_v2|mid)=(.*?)(?:;|$)', config.config["account"]["cookie"])
    return mid.group(2) if mid else None


def get_uid():
    uid = None
    uid_match = re.search(r"(account_id|ltuid|login_uid|ltuid_v2|account_id_v2)=(\d+)",
                          config.config["account"]["cookie"])
    if uid_match is None:
        return uid
    uid = uid_match.group(2)
    return uid


def get_stoken(login_ticket: str, uid: str) -> str:
    data = http.get(url=setting.bbs_get_multi_token_by_login_ticket,
                    params={"login_ticket": login_ticket, "token_types": "3", "uid": uid},
                    headers=headers).json()
    if data["retcode"] == 0:
        return data["data"]["list"][0]["token"]
    else:
        log.error("login_ticket（只有半小时有效期）已失效,请重新登录米游社抓取 cookie")
        config.clear_cookie()
        raise CookieError('Cookie expires')


def get_cookie_token_by_stoken():
    if config.config["account"]["stoken"] == "" and config.config["account"]["stuid"] == "":
        log.error("Stoken 和 Suid 为空，无法自动更新 CookieToken")
        config.clear_cookie()
        raise CookieError('Cookie expires')
    header = deepcopy(headers)
    header["cookie"] = get_stoken_cookie()
    data = http.get(url=setting.bbs_get_cookie_token_by_stoken,
                    headers=header).json()
    if data.get("retcode", -1) != 0:
        log.error("stoken 已失效，请重新抓取 cookie")
        config.clear_stoken()
        raise StokenError('Stoken expires')
    return data["data"]["cookie_token"]


def update_cookie_token() -> bool:
    log.info("CookieToken 失效，尝试刷新")
    old_token_match = re.search(r'cookie_token=(.*?)(?:;|$)', config.config["account"]["cookie"])
    if old_token_match:
        new_token = get_cookie_token_by_stoken()
        log.info("CookieToken 刷新成功")
        config.config["account"]["cookie"] = config.config["account"]["cookie"].replace(
            old_token_match.group(1), new_token)
        config.save_config()
        return True
    return False


def require_mid() -> bool:
    """
    判断是否需要mid

    :return: 是否需要mid
    """
    if config.config["account"]["stoken"].startswith("v2_"):
        return True
    return False


def get_stoken_cookie() -> str:
    """
    获取带stoken的cookie

    :return: 正确的stoken的cookie
    """
    cookie = f"stuid={config.config['account']['stuid']};stoken={config.config['account']['stoken']}"
    if require_mid():
        if config.config['account']['mid']:
            cookie += f";mid={config.config['account']['mid']}"
        else:
            log.error(f"v2_stoken 需要 mid 参数")
            raise CookieError(f"cookie require mid parament")
    return cookie
