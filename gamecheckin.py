import time
import login
import tools
import config
import random
import captcha
import setting
from error import *
from request import get_new_session
from loghelper import log
from account import get_account_list


class GameCheckin:

    def __init__(self, game_id: str, game_mid: str, game_name: str, act_id: str, player_name: str = "玩家") -> None:
        """
        游戏签到

        :param game_id: 游戏ID(米游社)
        :param game_mid: 游戏ID(配置文件)
        :param game_name: 游戏名称
        :param act_id: 签到活动ID
        :param player_name: 玩家称呼
        """
        self.game_id = game_id
        self.game_mid = game_mid
        self.game_name = game_name
        self.act_id = act_id
        self.player_name = player_name
        self.headers = {}
        self.http = get_new_session()

        self.set_headers()

        self.rewards_api = setting.cn_game_checkin_rewards
        self.account_list = self.get_account_list()
        self.is_sign_api = setting.cn_game_is_signurl

        self.sign_api = setting.cn_game_sign_url
        self.checkin_rewards = []

    def init(self):
        if len(self.account_list) != 0:
            self.checkin_rewards = self.get_checkin_rewards()

    def set_headers(self):
        headers = setting.headers.copy()
        headers['DS'] = tools.get_ds(web=True)
        headers['Referer'] = 'https://act.mihoyo.com/'
        headers['Cookie'] = config.config.get("account", {}).get("cookie", "")
        headers['x-rpc-device_id'] = config.config["device"]["id"]
        headers['User-Agent'] = tools.get_useragent(config.config["games"]["cn"]["useragent"])
        self.headers = headers

    def get_account_list(self) -> list:
        try:
            account_list = get_account_list(self.game_id, self.headers)
        except CookieError:
            log.warning(f"获取{self.game_name}账号列表失败！")
            config.clear_cookie()
            config.disable_games()
            raise CookieError("Cookie Error")
        return account_list

    # 获取签到信息
    def get_checkin_rewards(self) -> list:
        log.info("正在获取签到奖励列表...")
        max_retry = 3
        for i in range(max_retry):
            req = self.http.get(self.rewards_api, params={"act_id": self.act_id}, headers=self.headers)
            data = req.json()
            if data["retcode"] == 0:
                return data["data"]["awards"]
            log.warning(f"获取签到奖励列表失败，重试次数：{i + 1}")
            time.sleep(5)  # 等待5秒后重试
        log.warning("获取签到奖励列表失败")
        return []

    # 判断签到
    def is_sign(self, region: str, uid: str, update: bool = False) -> dict:
        req = self.http.get(self.is_sign_api, params={"act_id": self.act_id, "region": region, "uid": uid},
                            headers=self.headers)
        data = req.json()
        if data["retcode"] != 0:
            if not update and login.update_cookie_token():
                self.set_headers()
                return self.is_sign(region, uid, True)
            log.warning("获取账号签到信息失败！")
            print(req.text)
            config.config["games"]["cn"][self.game_mid]["auto_checkin"] = False
            config.save_config()
            raise CookieError("BBS Cookie Errror")
        return data["data"]

    def check_in(self, account):
        header = self.headers.copy()
        retries = config.config['games']['cn'].get('retries', 3)
        for i in range(1, retries + 1):
            if i > 1:
                log.info(f'触发验证码，即将进行第 {i} 次重试，最多 {retries} 次')
            req = self.http.post(url=self.sign_api, headers=header,
                                 json={'act_id': self.act_id, 'region': account[2], 'uid': account[1]})
            if req.status_code == 429:
                time.sleep(10)  # 429同ip请求次数过多，尝试sleep10s进行解决
                log.warning('429 Too Many Requests，即将进入下一次请求')
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
            log.info(f"正在为{self.player_name}「{account[0]}」进行签到...")
            time.sleep(random.randint(2, 8))
            is_data = self.is_sign(region=account[2], uid=account[1])
            if is_data.get("first_bind", False):
                log.warning(f"{self.player_name}「{account[0]}」是第一次绑定米游社，请先手动签到一次")
                continue
            sign_days = is_data["total_sign_day"] - 1
            if is_data["is_sign"]:
                log.info(f"{self.player_name}「{account[0]}」今天已经签到过了~\r\n今天获得的奖"
                         f"励是{tools.get_item(self.checkin_rewards[sign_days])}")
                sign_days += 1
            else:
                time.sleep(random.randint(2, 8))
                req = self.check_in(account)
                if req.status_code != 429:
                    data = req.json()
                    if data["retcode"] == 0 and data["data"]["success"] == 0:
                        log.info(
                            f"{self.player_name}「{account[0]}」签到成功~\r\n今天获得的奖励是"
                            f"{tools.get_item(self.checkin_rewards[0 if sign_days == 0 else sign_days + 1])}")
                        sign_days += 2
                    elif data["retcode"] == -5003:
                        log.info(
                            f"{self.player_name}{account[0]}今天已经签到过了~\r\n今天获得的奖励是"
                            f"{tools.get_item(self.checkin_rewards[sign_days])}")
                    else:
                        s = "账号签到失败！"
                        if data["data"] != "" and data.get("data").get("success", -1):
                            s += "原因：验证码\njson 信息：" + req.text
                        log.warning(s)
                        return_data += f"\n{account[0]}，触发验证码，本次签到失败"
                        continue
                else:
                    return_data += f"\n{account[0]}，本次签到失败"
                    continue
            return_data += f"\n{account[0]}已连续签到{sign_days}天\n" \
                           f"今天获得的奖励是{tools.get_item(self.checkin_rewards[sign_days - 1])}"
        return return_data


class Honkai2(GameCheckin):
    def __init__(self) -> None:
        super().__init__("bh2_cn", "honkai2", "崩坏学园2", setting.honkai2_act_id)
        self.headers['Referer'] = 'https://webstatic.mihoyo.com/bbs/event/signin/bh2/index.html?bbs_auth_required' \
                                  f'=true&act_id={setting.honkai2_act_id}&bbs_presentation_style=fullscreen' \
                                  '&utm_source=bbs&utm_medium=mys&utm_campaign=icon'
        self.init()


class Honkai3rd(GameCheckin):
    def __init__(self) -> None:
        super().__init__("bh3_cn", "honkai3rd", "崩坏3", setting.honkai3rd_act_id, "舰长")
        self.headers['Referer'] = 'https://webstatic.mihoyo.com/bbs/event/signin/bh3/index.html?bbs_auth_required' \
                                  f'=true&act_id={setting.honkai3rd_act_id}&bbs_presentation_style=fullscreen' \
                                  '&utm_source=bbs&utm_medium=mys&utm_campaign=icon'
        self.init()


class TearsOfThemis(GameCheckin):
    def __init__(self) -> None:
        super().__init__("nxx_cn", "tears_of_themis", "未定事件簿", setting.tearsofthemis_act_id, "律师")
        self.headers['Referer'] = 'https://webstatic.mihoyo.com/bbs/event/signin/nxx/index.html?bbs_auth_required' \
                                  '=true&bbs_presentation_style=fullscreen' \
                                  f'act_id={setting.tearsofthemis_act_id}'
        self.init()


class Genshin(GameCheckin):
    def __init__(self) -> None:
        super().__init__("hk4e_cn", "genshin", "原神", setting.genshin_act_id, "旅行者")
        self.headers["Origin"] = "https://act.mihoyo.com"
        self.headers["x-rpc-signgame"] = "hk4e"
        self.init()


class Honkaisr(GameCheckin):
    def __init__(self):
        super().__init__("hkrpg_cn", "honkai_sr", "崩坏：星穹铁道", setting.honkai_sr_act_id, "开拓者")
        self.headers["Origin"] = "https://act.mihoyo.com"
        self.init()


class ZZZ(GameCheckin):
    def __init__(self):
        super().__init__("nap_cn", "zzz", "绝区零", setting.zzz_act_id, "绳匠")
        self.headers["Origin"] = "https://act.mihoyo.com"
        self.headers['X-Rpc-Signgame'] = 'zzz'
        self.rewards_api = setting.zzz_game_checkin_rewards
        self.is_sign_api = setting.zzz_game_is_signurl
        self.sign_api = setting.zzz_game_sign_url
        self.init()


def checkin_game(game_name, game_module, game_print_name=""):
    game_config = config.config["games"]["cn"][game_name]
    if game_config["checkin"]:
        time.sleep(random.randint(2, 8))
        if game_print_name == "":
            game_print_name = game_name
        log.info(f"正在进行「{game_print_name}」签到")
        return_data = f"\n\n{game_module().sign_account()}"
        return return_data
    return ''


def run_task():
    games = [
        ("崩坏学园2", "honkai2", Honkai2),
        ("崩坏3rd", "honkai3rd", Honkai3rd),
        ("未定事件簿", "tears_of_themis", TearsOfThemis),
        ("原神", "genshin", Genshin),
        ("崩坏：星穹铁道", "honkai_sr", Honkaisr),
        ("绝区零", "zzz", ZZZ)
    ]
    return_data = ''
    for game_print_name, game_name, game_module in games:
        return_data += checkin_game(game_name, game_module, game_print_name)
    return return_data
