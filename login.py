import json
import re
from copy import deepcopy

import config
import setting
import tools
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


def exchange_token_by_stoken(target: int) -> str:
    """
    通行证 V2 换票：用 SToken 换取 LToken / CookieToken。

    :param target: 2 为 LToken，4 为 CookieToken
    :return: 换到的 token 字符串
    """
    stoken = config.config["account"]["stoken"]
    mid = config.config["account"]["mid"]
    if not stoken:
        raise StokenError('no stoken')
    if not mid:
        log.error("v2 换票需要 mid 参数，请重新抓取 cookie")
        raise CookieError("cookie require mid parament")

    body = json.dumps(
        {
            "dst_token_type": target,
            "src_token": {"token": stoken, "token_type": 1},
            "mid": mid,
        },
        separators=(",", ":"),
    )
    time_stamp = tools.timestamp()
    nonce = tools.random_text(6)
    digest = tools.md5(
        f"salt={setting.mihoyobbs_salt_passport}&t={time_stamp}&r={nonce}&b={body}&q=")

    device = config.config["device"]
    req_headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "DS": f"{time_stamp},{nonce},{digest}",
        "x-rpc-app_id": setting.mihoyobbs_app_id,
        "x-rpc-client_type": "2",
        "x-rpc-app_version": setting.mihoyobbs_version,
        "x-rpc-game_biz": "bbs_cn",
        "x-rpc-sys_version": "12",
        "x-rpc-sdk_version": setting.mihoyobbs_passport_version,
        "x-rpc-account_version": setting.mihoyobbs_passport_version,
        "x-rpc-lifecycle_id": tools.get_lifecycle_id(),
        "x-rpc-device_id": device.get("id", ""),
        "x-rpc-device_name": device.get("name", ""),
        "x-rpc-device_model": device.get("model", ""),
        "User-Agent": "okhttp/4.9.3",
    }
    if device.get("fp", "") != "":
        req_headers["x-rpc-device_fp"] = device["fp"]

    data = http.post(url=setting.passport_exchange_url,
                     headers=req_headers, data=body.encode("utf-8")).json()
    if data.get("retcode", -1) != 0:
        log.error(f"换票失败，retcode={data.get('retcode')}，message={data.get('message')}")
        if data.get("retcode") in (-100, -3260):
            config.clear_stoken()
            raise StokenError('Stoken expires')
        raise CookieError(f"exchange token failed: {data.get('message')}")

    token = (data.get("data") or {}).get("token") or {}
    value = token.get("token")
    if not value:
        log.error("换票响应缺少 token")
        raise CookieError("exchange token response missing token")
    return value


def get_ltoken_by_stoken_v2() -> str:
    """用 SToken 兑换 LToken（dst_token_type=2）"""
    return exchange_token_by_stoken(2)


def get_cookie_token_by_stoken_v2() -> str:
    """用 SToken 兑换 CookieToken（dst_token_type=4）"""
    return exchange_token_by_stoken(4)


def update_cookie_token() -> bool:
    """刷新 CookieToken，并原地写回配置里的 cookie 字符串。

    有 mid 时走 V2 exchange（dst_token_type=4），否则回退旧接口。
    """
    log.info("CookieToken 失效，尝试刷新")
    current = config.config["account"].get("cookie", "")
    fields = parse_cookie(current)
    if not any(k.startswith("cookie_token") for k in fields):
        log.warning("当前 cookie 中不存在 cookie_token 字段，无法刷新")
        return False

    use_v2 = require_mid()
    try:
        new_token = get_cookie_token_by_stoken_v2() if use_v2 else get_cookie_token_by_stoken()
    except (CookieError, StokenError):
        raise

    key = "cookie_token_v2" if (use_v2 or "cookie_token_v2" in fields) else "cookie_token"
    fields[key] = new_token
    if use_v2:
        fields.setdefault("account_id_v2", config.config["account"]["stuid"])
        fields.setdefault("account_mid_v2", config.config["account"]["mid"])
    # V2 存在时让 cookie_token / account_id 等旧名与 V2 同值
    sync_cookie_aliases(fields)

    config.config["account"]["cookie"] = format_cookie(fields)
    log.info("CookieToken 刷新成功")
    config.save_config()
    return True


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


def build_account_cookie() -> str:
    """
    生成 BBS 业务所需的完整 Cookie。

    """
    base = config.config.get("account", {}).get("cookie", "")
    if not base or base == "CookieError":
        raise CookieError("请先填入 cookie")

    fields = parse_cookie(base)
    stuid = config.config["account"]["stuid"]
    mid = config.config["account"]["mid"]
    changed = False

    # ltoken / ltuid / mid：缺失则兑换一次 LToken
    if not fields.get("ltoken_v2") and not fields.get("ltoken"):
        try:
            ltoken = get_ltoken_by_stoken_v2()
        except CookieError as e:
            log.warning(f"补齐 LToken 失败：{e}")
        else:
            fields["ltoken_v2"] = ltoken
            fields["ltuid_v2"] = stuid
            fields["ltmid_v2"] = mid
            changed = True

    # cookie_token：缺失则兑换一次 CookieToken
    if not fields.get("cookie_token_v2") and not fields.get("cookie_token"):
        try:
            cookie_token = get_cookie_token_by_stoken_v2()
        except CookieError as e:
            log.warning(f"补齐 CookieToken 失败：{e}")
        else:
            fields["cookie_token_v2"] = cookie_token
            fields["account_id_v2"] = stuid
            fields["account_mid_v2"] = mid
            changed = True

    if changed:
        fields.setdefault("ltuid_v2", stuid)
        fields.setdefault("ltmid_v2", mid)
        fields.setdefault("account_id_v2", stuid)
        fields.setdefault("account_mid_v2", mid)
        config.config["account"]["cookie"] = format_cookie(fields)
        config.save_config()

    # V2 存在时让旧名字段与其同值
    if sync_cookie_aliases(fields):
        config.config["account"]["cookie"] = format_cookie(fields)
        config.save_config()

    return format_cookie(fields)


_COOKIE_ORDER = (
    "ltoken", "ltuid", "account_id", "cookie_token", "login_ticket",
    "ltoken_v2", "ltuid_v2", "ltmid_v2",
    "cookie_token_v2", "account_id_v2", "account_mid_v2",
)

# V2 字段存在时，旧名字段与其同值（米游社 App CookieTokenPresenter#f 即如此）
_V2_TO_V1_ALIASES = (
    ("ltoken_v2", "ltoken"),
    ("ltuid_v2", "ltuid"),
    ("account_id_v2", "account_id"),
    ("cookie_token_v2", "cookie_token"),
)


def sync_cookie_aliases(fields: dict) -> bool:
    """V2 字段存在时，把旧名字段同步成同一个值。

    米游社 App 注入 WebView 时 `ltoken` 与 `ltoken_v2`、`cookie_token` 与
    `cookie_token_v2` 写的是同一个 token（见 CookieTokenPresenter$Companion#f），
    这样新旧页面都能读到有效凭据，也不会残留失效的 V1 旧值。

    :return: 是否有字段被改动
    """
    changed = False
    for v2_key, v1_key in _V2_TO_V1_ALIASES:
        value = fields.get(v2_key)
        if value and fields.get(v1_key) != value:
            fields[v1_key] = value
            changed = True
    return changed


def parse_cookie(cookie: str) -> dict:
    """把 cookie 字符串解析成 dict（忽略空值）。"""
    result = {}
    for segment in re.split(r"[;\r\n]+", cookie or ""):
        text = segment.strip()
        if not text or "=" not in text:
            continue
        key, value = text.split("=", 1)
        key, value = key.strip(), value.strip()
        if key and value:
            result[key] = value
    return result


def format_cookie(fields: dict) -> str:
    """按固定顺序把 dict 拼回 cookie 字符串。"""
    ordered = [k for k in _COOKIE_ORDER if fields.get(k)]
    ordered += [k for k in fields if k not in _COOKIE_ORDER and fields[k]]
    return ";".join(f"{k}={fields[k]}" for k in ordered) + ";"

