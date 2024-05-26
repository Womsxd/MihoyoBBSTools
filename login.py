import re

import config
import setting
from error import CookieError
from loghelper import log
from request import http

headers = setting.headers.copy()
headers.pop("DS")
headers.pop("Origin")
headers.pop("Referer")


def login():
    if not config.config["account"]["cookie"]:
        log.error("请填入Cookies!")
        config.clear_cookies()
        raise CookieError('No cookie')
    if config.config['account']['stoken'] == "":
        log.error("无Stoken 请手动填入stoken!")
        raise CookieError('no stoken')
    # # 判断Cookie里面是否有login_ticket 没有的话直接退了
    # login_ticket = get_login_ticket()
    # if login_ticket is None:
    #     log.error("cookie中没有'login_ticket'字段,请重新登录米游社，重新抓取cookie!")
    #     config.clear_cookies()
    #     raise CookieError('Cookie lost login_ticket')
    uid = get_uid()
    if uid is None:
        log.error("cookie已失效,请重新登录米游社抓取cookie")
        config.clear_cookies()
        raise CookieError('Cookie expires')
    config.config["account"]["stuid"] = uid
    # config.config["account"]["stoken"] = get_stoken(login_ticket, uid)
    if require_mid():
        config.config["account"]["mid"] = get_mid()
    log.info("登录成功！")
    log.info("正在保存Config！")
    config.save_config()


def get_login_ticket() -> str:
    ticket_match = re.search(r'login_ticket=(.*?)(?:;|$)', config.config["account"]["cookie"])
    return ticket_match.group(1) if ticket_match else None


def get_mid() -> str:
    mid = re.search(r'(account_mid_v2|ltmid_v2|mid)=(.*?)(?:;|$)', config.config["account"]["cookie"])
    return mid.group(2) if mid else None


def get_uid() -> str:
    uid = None
    uid_match = re.search(r"(account_id|ltuid|login_uid)=(\d+)", config.config["account"]["cookie"])
    if uid_match is None:
        # stuid就是uid，先搜索cookie里面的，搜不到再用api获取
        data = http.get(url=setting.bbs_account_info,
                        params={"login_ticket": config.config["account"]["login_ticket"]},
                        headers=headers).json()
        if "成功" in data["data"]["msg"]:
            uid = str(data["data"]["cookie_info"]["account_id"])
    else:
        uid = uid_match.group(2)
    return uid


def get_stoken(login_ticket: str, uid: str) -> str:
    data = http.get(url=setting.bbs_get_multi_token_by_login_ticket,
                    params={"login_ticket": login_ticket, "token_types": "3", "uid": uid},
                    headers=headers).json()
    if data["retcode"] == 0:
        return data["data"]["list"][0]["token"]
    else:
        log.error("login_ticket(只有半小时有效期)已失效,请重新登录米游社抓取cookie")
        config.clear_cookies()
        raise CookieError('Cookie expires')


def get_cookie_token_by_stoken():
    if config.config["account"]["stoken"] == "" and config.config["account"]["stuid"] == "":
        log.error("Stoken和Suid为空，无法自动更新CookieToken")
        config.clear_cookies()
        raise CookieError('Cookie expires')
    data = http.get(url=setting.bbs_get_cookie_token_by_stoken,
                    params={"stoken": config.config["account"]["stoken"], "uid": config.config["account"]["stuid"]},
                    headers=headers).json()
    if data.get("retcode", -1) != 0:
        log.error("stoken已失效，请重新抓取cookie")
        config.clear_cookies()
        raise CookieError('Cookie expires')
    return data["data"]["cookie_token"]


def update_cookie_token() -> bool:
    log.info("CookieToken失效，尝试刷新")
    old_token_match = re.search(r'cookie_token=(.*?)(?:;|$)', config.config["account"]["cookie"])
    if old_token_match:
        new_token = get_cookie_token_by_stoken()
        log.info("CookieToken刷新成功")
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
            log.error(f"v2_stoken需要mid参数")
            raise CookieError(f"cookie require @mid parament")
    return cookie
