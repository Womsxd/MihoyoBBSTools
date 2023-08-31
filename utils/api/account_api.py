'''
Author: Night-stars-1 nujj1042633805@gmail.com
Date: 2023-08-26 00:42:54
LastEditors: Night-stars-1 nujj1042633805@gmail.com
LastEditTime: 2023-08-31 16:05:29
Description: 

Copyright (c) 2023 by Night-stars-1, All Rights Reserved. 
'''
"""
### 米游社的游戏账号相关API
"""
from typing import Tuple

from ..config import ConfigManager
from ..data_model import AccountResult, BBSCookies, ApiResultHandler
from ..error import CookieError
from ..request import *
from ..utils import get_ds, log
from tenacity import RetryError, Retrying, stop_after_attempt

_conf = ConfigManager.data_obj

ACCOUNT_INFO_URL = "https://api-takumi.miyoushe.com/binding/api/getUserGameRolesByStoken?game_biz="
LTOKEN_BY_STOKEN_URL = "https://passport-api.mihoyo.com/account/auth/api/getLTokenBySToken"

# 游戏账号相关API的请求头
headers = {
    'Accept': 'application/json, text/plain, */*',
    "x-rpc-channel": "miyousheluodi",
    'Origin': 'https://webstatic.mihoyo.com',
    'x-rpc-app_version': _conf.salt.mihoyobbs_version,
    'User-Agent': 'Mozilla/5.0 (Linux; Android 13; 21121210C Build/TKQ1.220807.001; wv) AppleWebKit/537.36 (KHTML, like Gecko) '
                f'Version/4.0 Chrome/115.0.5790.166 Mobile Safari/537.36 miHoYoBBS/{_conf.salt.mihoyobbs_version}',
    'x-rpc-client_type': "5",
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'zh-CN,en-US;q=0.8',
    'X-Requested-With': 'com.mihoyo.hyperion',
}
async def get_account_list(game_biz: str) -> list[AccountResult]:
    log.info(f"正在获取米哈游账号绑定的账号列表...")
    account_list = []
    acc_headers = headers.copy()
    acc_headers['DS'] = get_ds(web=True)
    req = await get(ACCOUNT_INFO_URL + game_biz,
                    headers=acc_headers,
                    cookies=_conf.mhy_data.cookie.dict())
    data = req.json()
    if data["retcode"] != 0:
        log.warning(f"获取账号列表失败！")
        raise CookieError("BBS Cookie Error")
    for i in data["data"]["list"]:
        account_list.append(AccountResult.parse_obj(i))
    log.info(f"已获取到{len(account_list)}个账号信息")
    return account_list

async def get_ltoken_by_stoken(cookies: BBSCookies) -> Tuple[bool, Optional[BBSCookies]]:
    """
    通过 stoken_v2 和 mid 获取 ltoken

    :param cookies: 米游社Cookies，需要包含 stoken_v2 和 mid
    :param device_id: X_RPC_DEVICE_ID
    :param retry: 是否允许重试
    """
    try:
        for attempt in Retrying(stop=stop_after_attempt(3)):
            with attempt:
                lbs_headers = headers.copy()
                res = await get(
                    LTOKEN_BY_STOKEN_URL,
                    cookies=cookies.dict(cookie_type=True),
                    headers=lbs_headers,
                    timeout=_conf.preference.timeout)
                api_result = ApiResultHandler(res.json())
                log.info(api_result)
                if api_result.success:
                    cookies.ltoken = api_result.data["ltoken"]
                    return True, cookies
                elif api_result.login_expired:
                    log.warning("通过 stoken 获取 ltoken: 登录失效")
                    return False, None
                else:
                    raise CookieError("BBS Cookie Error")

    except RetryError as e:
        log.exception("通过 stoken 获取 ltoken: 网络请求失败")
        return False, None