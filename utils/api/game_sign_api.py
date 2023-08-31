'''
Author: Night-stars-1 nujj1042633805@gmail.com
Date: 2023-08-26 00:15:46
LastEditors: Night-stars-1 nujj1042633805@gmail.com
LastEditTime: 2023-08-31 15:00:49
Description: 

Copyright (c) 2023 by Night-stars-1, All Rights Reserved. 
'''
"""
### 米游社的游戏签到相关API
"""
import uuid
from typing import Set, Type
from urllib.parse import urlencode

from tenacity import RetryError, Retrying, stop_after_attempt

from ..config import ConfigManager
from ..data_model import (AccountResult, ApiResultHandler, BaseApiStatus,
                          GeetestResult)
from ..error import CaptchaError
from ..request import get, post
from ..utils import (get_ds, get_validate, is_incorrect_return,
                     log)

_conf = ConfigManager.data_obj

class BaseGameSign:
    """
    游戏签到基类
    """
    NAME = ""
    """游戏名字"""

    ACT_ID = ""
    URL_REWARD = "https://api-takumi.mihoyo.com/event/luna/home"
    URL_INFO = "https://api-takumi.mihoyo.com/event/luna/info"
    URL_SIGN = "https://api-takumi.mihoyo.com/event/luna/sign"
    GAME_ID = 0
    GAME_BIZ = ""

    AVAILABLE_GAME_SIGNS: Set[Type["BaseGameSign"]] = set()
    """可用的子类"""

    def __init__(self, account: AccountResult):
        self.account = account
        reward_params = {
            "lang": "zh-cn",
            "act_id": self.ACT_ID
        }
        self.URL_REWARD = f"{self.URL_REWARD}?{urlencode(reward_params)}"
        info_params = {
            "lang": "zh-cn",
            "act_id": self.ACT_ID,
            "region": self.account.region,
            "uid": self.account.game_uid
        }
        self.URL_INFO = f"{self.URL_INFO}?{urlencode(info_params)}"
        self.headers = {
            'Accept': 'application/json, text/plain, */*',
            'DS': get_ds(web=True),
            "x-rpc-channel": "miyousheluodi",
            'Origin': 'https://webstatic.mihoyo.com',
            'x-rpc-app_version': _conf.salt.mihoyobbs_version,
            'User-Agent': 'Mozilla/5.0 (Linux; Android 12; Unspecified Device) AppleWebKit/537.36 (KHTML, like Gecko) '
                        f'Version/4.0 Chrome/103.0.5060.129 Mobile Safari/537.36 miHoYoBBS/{_conf.salt.mihoyobbs_version}',
            'x-rpc-client_type': "5",
            'Referer': '',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,en-US;q=0.8',
            'X-Requested-With': 'com.mihoyo.hyperion',
            'x-rpc-device_id': uuid.uuid4().hex
        }

    async def sign(self) -> BaseApiStatus:
        """
        签到
        """
        content = {
            "act_id": self.ACT_ID,
            "region": self.account.region,
            "uid": self.account.game_uid
        }
        challenge = ""
        """人机验证任务 challenge"""
        geetest_result = GeetestResult("", "")
        """人机验证结果"""

        try:
            for attempt in Retrying(stop=stop_after_attempt(3)):
                with attempt:
                    if geetest_result.validate:
                        self.headers["x-rpc-validate"] = geetest_result.validate
                        self.headers["x-rpc-challenge"] = challenge
                        self.headers["x-rpc-seccode"] = f'{geetest_result.validate}|jordan'

                    res = await post(
                        self.URL_SIGN,
                        headers=self.headers,
                        cookies=_conf.mhy_data.cookie.dict(),
                        timeout=_conf.preference.timeout,
                        json=content
                    )

                    api_result = ApiResultHandler(res.json())
                    if api_result.login_expired:
                        log.info(
                            f"游戏签到 - 用户 {self.account.game_uid} 登录失效")
                        log.debug(f"网络请求返回: {res.text}")
                        return BaseApiStatus(login_expired=True)
                    if api_result.invalid_ds:
                        log.info(
                            f"游戏签到 - 用户 {self.account.game_uid} DS 校验失败")
                        log.debug(f"网络请求返回: {res.text}")
                        return BaseApiStatus(invalid_ds=True)
                    if api_result.data.get("risk_code") != 0:
                        log.warning(
                            f"游戏签到 - 用户 {self.account.game_uid} 可能被人机验证阻拦")
                        log.debug(f"网络请求返回: {res.text}")
                        gt = api_result.data.get("gt", None)
                        challenge = api_result.data.get("challenge", None)
                        if gt and challenge:
                            log.info(_conf.preference.geetest_url)
                            if _conf.preference.geetest_url:
                                geetest_result = await get_validate(gt, challenge)
                                raise CaptchaError("Captcha Error")
                            else:
                                return BaseApiStatus(need_verify=True)
            return BaseApiStatus(success=True)

        except RetryError as e:
            if is_incorrect_return(e):
                log.exception(f"游戏签到 - 服务器没有正确返回")
                log.debug(f"网络请求返回: {res.text}")
                return BaseApiStatus(incorrect_return=True)
            elif isinstance(e.last_attempt._exception, CaptchaError):
                log.error(f"游戏签到 - 验证码错误")
                return BaseApiStatus(captcha_error=True)
            else:
                log.exception(f"游戏签到 - 请求失败")
                return BaseApiStatus(network_error=True)


class GenshinImpactSign(BaseGameSign):
    """
    原神 游戏签到
    """
    NAME = "原神"
    ACT_ID = "e202009291139501"
    GAME_ID = 2
    GAME_BIZ = "hk4e_cn"
    URL_REWARD = "https://api-takumi.mihoyo.com/event/bbs_sign_reward/home"
    URL_INFO = "https://api-takumi.mihoyo.com/event/bbs_sign_reward/info"
    URL_SIGN = "https://api-takumi.mihoyo.com/event/bbs_sign_reward/sign"


class HonkaiImpact3Sign(BaseGameSign):
    """
    崩坏3 游戏签到
    """
    NAME = "崩坏3"
    ACT_ID = "e202207181446311"
    GAME_ID = 1


class HoukaiGakuen2Sign(BaseGameSign):
    """
    崩坏学园2 游戏签到
    """
    NAME = "崩坏学园2"
    ACT_ID = "e202203291431091"
    GAME_ID = 3


class TearsOfThemisSign(BaseGameSign):
    """
    未定事件簿 游戏签到
    """
    NAME = "未定事件簿"
    ACT_ID = "e202202251749321"
    GAME_ID = 4


class StarRailSign(BaseGameSign):
    """
    崩坏：星穹铁道 游戏签到
    """
    NAME = "崩坏：星穹铁道"
    ACT_ID = "e202304121516551"
    GAME_ID = 6


BaseGameSign.AVAILABLE_GAME_SIGNS.add(GenshinImpactSign)
#BaseGameSign.AVAILABLE_GAME_SIGNS.add(HonkaiImpact3Sign)
#BaseGameSign.AVAILABLE_GAME_SIGNS.add(HoukaiGakuen2Sign)
#BaseGameSign.AVAILABLE_GAME_SIGNS.add(TearsOfThemisSign)
#BaseGameSign.AVAILABLE_GAME_SIGNS.add(StarRailSign)
