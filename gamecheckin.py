import time
import login
import tools
import config
import random
import captcha
import setting
from error import *
from request import http
from loghelper import log
from account import get_account_list


class GameCheckin:
    def __init__(self, game_id) -> None:
        self.headers = self._get_headers()
        self.game_id = game_id
        self.rewards_api = setting.cn_game_checkin_rewards
        self.account_list = self._get_account_list()
        self.is_sign_api = setting.cn_game_is_signurl
        self.game_mid = ""
        self.game_name = ""
        self.sign_api = setting.cn_game_sign_url
        self.act_id = ""
        self.player_name = "玩家"
        self.checkin_rewards = []

    def init(self):
        if len(self.account_list) != 0:
            self.checkin_rewards = self.get_checkin_rewards()

    def _get_headers(self) -> dict:
        headers = setting.headers.copy()
        headers['DS'] = tools.get_ds(web=True)
        headers['Cookie'] = config.config.get("account", {}).get("cookie", "")
        headers['x-rpc-device_id'] = tools.get_device_id()
        headers['User-Agent'] = tools.get_useragent()
        return headers

    def _get_account_list(self, update: bool = False) -> list:
        account_list = get_account_list(self.game_id, self.headers)
        if account_list is None:
            if not update and login.update_cookie_token():
                self.headers = self._get_headers()
                return self._get_account_list()
            log.warning(f"获取{self.game_name}账号列表失败！")
            config.clear_cookie_game(self.game_id)
            raise CookieError("BBS Cookie Error")
        return account_list

    # 获取签到信息
    def get_checkin_rewards(self) -> list:
        log.info("正在获取签到奖励列表...")
        max_retry = 3
        for i in range(max_retry):
            req = http.get(self.rewards_api, params={"act_id": self.act_id}, headers=self.headers)
            data = req.json()
            if data["retcode"] == 0:
                return data["data"]["awards"]
            else:
                log.warning(f"获取签到奖励列表失败，重试次数: {i + 1}")
                time.sleep(5)  # 等待5秒后重试
        log.warning("获取签到奖励列表失败")
        return []

    # 判断签到
    def is_sign(self, region: str, uid: str, update: bool = False) -> dict:
        req = http.get(self.is_sign_api, params={"act_id": self.act_id, "region": region, "uid": uid},
                       headers=self.headers)
        data = req.json()
        if data["retcode"] != 0:
            if not update and login.update_cookie_token():
                self.headers = self._get_headers()
                return self.is_sign(region, uid, True)
            log.warning("获取账号签到信息失败！")
            print(req.text)
            config.config["games"]["cn"][self.game_mid]["auto_checkin"] = False
            config.save_config()
            raise CookieError("BBS Cookie Errror")
        return data["data"]

    def check_in(self, account):
        header = self.headers.copy()
        retries = 3
        for i in range(1, retries + 1):
            if i > 1:
                log.info(f'触发验证码，即将进行第 {i} 次重试，最多 {retries} 次')
            req = http.post(url=self.sign_api, headers=header,
                            json={'act_id': self.act_id, 'region': account[2], 'uid': account[1]})
            if req.status_code == 429:
                time.sleep(10)  # 429同ip请求次数过多，尝试sleep10s进行解决
                log.warning('429 Too Many Requests ，即将进入下一次请求')
                continue
            data = req.json()
            if data["retcode"] == 0 and data["data"]["success"] == 1 and i < retries:
                validate = captcha.game_captcha(data["data"]["gt"], data["data"]["challenge"])
                if validate:
                    header.update({
                        "x-rpc-challenge": data["data"]["challenge"],
                        "x-rpc-validate": validate,
                        "x-rpc-seccode": f'{validate}|jordan'
                    })
                time.sleep(random.randint(6, 15))
            else:
                break
        return req

    def sign_account(self) -> str:
        return_data = f"{self.game_name}: "
        if not self.account_list:
            log.warning(f"账号没有绑定任何{self.game_name}账号！")
            return_data += f"\n并没有绑定任何{self.game_name}账号"
            return return_data
        for account in self.account_list:
            if account[1] in config.config["games"]["cn"][self.game_mid]["black_list"]:
                continue
            log.info(f"正在为{self.player_name}{account[0]}进行签到...")
            time.sleep(random.randint(2, 8))
            is_data = self.is_sign(region=account[2], uid=account[1])
            if is_data.get("first_bind", False):
                log.warning(f"{self.player_name}{account[0]}是第一次绑定米游社，请先手动签到一次")
            else:
                sign_days = is_data["total_sign_day"] - 1
                if is_data["is_sign"]:
                    log.info(f"{self.player_name}{account[0]}今天已经签到过了~\r\n今天获得的奖"
                             f"励是{tools.get_item(self.checkin_rewards[sign_days])}")
                    sign_days += 1
                else:
                    time.sleep(random.randint(2, 8))
                    req = self.check_in(account)
                    if req.status_code != 429:
                        data = req.json()
                        if data["retcode"] == 0 and data["data"]["success"] == 0:
                            log.info(
                                f"{self.player_name}{account[0]}签到成功~\r\n今天获得的奖励是"
                                f"{tools.get_item(self.checkin_rewards[0 if sign_days == 0 else sign_days + 1])}")
                            sign_days += 2
                        elif data["retcode"] == -5003:
                            log.info(
                                f"{self.player_name}{account[0]}今天已经签到过了~\r\n今天获得的奖励是"
                                f"{tools.get_item(self.checkin_rewards[sign_days])}")
                        else:
                            s = "账号签到失败！"
                            if data["data"] != "" and data.get("data").get("success", -1):
                                s += "原因: 验证码\njson信息:" + req.text
                            log.warning(s)
                            return_data += f"\n{account[0]}，触发验证码，本次签到失败"
                            continue
                    else:
                        return_data += f"\n{account[0]}，本次签到失败"
                        continue
            return_data += f"\n{account[0]}已连续签到{sign_days}天\n" \
                           f"今天获得的奖励是{tools.get_item(self.checkin_rewards[sign_days - 1])}"
        return return_data
