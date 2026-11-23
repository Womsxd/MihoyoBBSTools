import json
import random
import time
from copy import deepcopy

import captcha
import config
import login
import setting
import tools
from error import StokenError
from loghelper import log
from request import http


def wait():
    time.sleep(random.randint(3, 8))


class Mihoyobbs:
    def __init__(self):
        self.today_get_coins = 0
        self.today_have_get_coins = 0
        self.have_coins = 0
        self.bbs_config = config.config["mihoyobbs"]
        self.bbs_list = [setting.mihoyobbs_List.get(i) for i in self.bbs_config["checkin_list"]
                         if setting.mihoyobbs_List.get(i) is not None]
        self.headers = {
            "DS": tools.get_ds(web=False),
            "cookie": login.get_stoken_cookie(),
            "x-rpc-client_type": setting.mihoyobbs_Client_type,
            "x-rpc-app_version": setting.mihoyobbs_version,
            "x-rpc-sys_version": "12",
            "x-rpc-channel": "miyousheluodi",
            "x-rpc-device_id": config.config["device"]["id"],
            "x-rpc-device_name": config.config["device"]["name"],
            "x-rpc-device_model": config.config["device"]["model"],
            "x-rpc-h265_supported": "1",
            "Referer": "https://app.mihoyo.com",
            "x-rpc-verify_key": setting.mihoyobbs_verify_key,
            "x-rpc-csm_source": "discussion",
            "Content-Type": "application/json; charset=UTF-8",
            "Host": "bbs-api.miyoushe.com",
            "Connection": "Keep-Alive",
            "Accept-Encoding": "gzip",
            "User-Agent": "okhttp/4.9.3"
        }
        self.task_header = {
            'Accept': 'application/json, text/plain, */*',
            'Origin': 'https://webstatic.mihoyo.com',
            'User-Agent': 'Mozilla/5.0 (Linux; Android 12; Unspecified Device) AppleWebKit/537.36 (KHTML, like Gecko) '
                          f'Version/4.0 Chrome/103.0.5060.129 Mobile Safari/537.36 miHoYoBBS/{setting.mihoyobbs_version}',
            'Referer': 'https://webstatic.mihoyo.com',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,en-US;q=0.8',
            'X-Requested-With': 'com.mihoyo.hyperion',
            "Cookie": config.config.get("account", {}).get("cookie", ""),
        }
        if config.config["device"]["fp"] != "":
            self.headers["x-rpc-device_fp"] = config.config["device"]["fp"]
        self.task_do = {
            "sign": False
        }
        self.get_tasks_list()

    def get_pass_challenge(self):
        req = http.get(url=setting.bbs_get_captcha, headers=self.headers)
        data = req.json()
        if data["retcode"] != 0:
            return None
        captcha_result = captcha.bbs_captcha(data["data"]["gt"], data["data"]["challenge"])
        if captcha_result is not None:
            challenge = data["data"]["challenge"]
            if type(captcha_result) == dict:
                validate = captcha_result["validate"]
                challenge = captcha_result["challenge"]
            else:
                validate = captcha_result

            check_req = http.post(url=setting.bbs_captcha_verify, headers=self.headers,
                                  json={"geetest_challenge": challenge,
                                        "geetest_seccode": validate + "|jordan",
                                        "geetest_validate": validate})
            check = check_req.json()
            if check["retcode"] == 0:
                return check["data"]["challenge"]
        return None

    # 获取任务列表，用来判断做了哪些任务
    def get_tasks_list(self, update=False):
        log.info("正在获取任务列表")
        req = http.get(url=setting.bbs_tasks_list, params={"point_sn": "myb"}, headers=self.task_header)
        data = req.json()
        if "err" in data["message"] or data["retcode"] == -100:
            if not update and login.update_cookie_token():
                self.task_header['Cookie'] = config.config['account']['cookie']
                return self.get_tasks_list(True)
            else:
                log.error("获取任务列表失败，你的 cookie 可能已过期，请重新设置 cookie。")
                config.clear_cookie()
                raise StokenError('Cookie expires')
        self.today_get_coins = data["data"]["can_get_points"]
        self.today_have_get_coins = data["data"]["already_received_points"]
        self.have_coins = data["data"]["total_points"]
        tasks = {
            58: {"attr": "sign", "done": "is_get_award"},
        }
        if self.today_get_coins == 0:
            self.task_do["sign"] = True
        else:
            missions = data["data"]["states"]
            for task in tasks.keys():
                mission_state = next((x for x in missions if x["mission_id"] == task), None)
                if mission_state is None:
                    continue
                do = tasks[task]
                if mission_state[do["done"]]:
                    self.task_do[do["attr"]] = True
                elif do.get("num_attr") is not None:
                    self.task_do[do["num_attr"]] = self.task_do[do["num_attr"]] - mission_state["happened_times"]
        if data['data']['can_get_points'] != 0:
            if len(data['data']['states']) == 0:
                log.info(f"今天可以获得 {self.today_get_coins} 个米游币")
            else:
                new_day = data['data']['states'][0]['mission_id'] >= 62
                log.info(f"{'新的一天，今天可以获得' if new_day else '似乎还有任务没完成，今天还能获得'}"
                        f" {self.today_get_coins} 个米游币")

    # 进行签到操作
    def signing(self):
        if self.task_do["sign"]:
            log.info("讨论区任务已经完成过了~")
            return
        log.info("正在签到......")
        header = self.headers.copy()
        for forum in self.bbs_list:
            challenge = None
            for retry_count in range(2):
                post_data = json.dumps({"gids": forum["id"]})
                post_data.replace(' ', '')
                header["DS"] = tools.get_ds2("", post_data)
                req = http.post(url=setting.bbs_sign_url, data=post_data, headers=header)
                log.debug(req.text)
                data = req.json()
                if data["retcode"] == 1034:
                    log.warning("社区签到触发验证码")
                    challenge = self.get_pass_challenge()
                    if challenge is not None:
                        header["x-rpc-challenge"] = challenge
                elif "err" not in data["message"] and data["retcode"] == 0:
                    log.info(str(forum["name"] + data["message"]))
                    wait()
                    break
                elif data["retcode"] == -100:
                    log.error("签到失败，你的 cookie 可能已过期，请重新设置 cookie。")
                    config.clear_stoken()
                    raise StokenError('Stoken expires')
                else:
                    log.error(f'未知错误：{req.text}')
            if challenge is not None:
                header.pop("x-rpc-challenge")

    def run_task(self):
        return_data = "米游社: "
        if self.task_do["sign"]:
            return_data += "\n" + f"今天已经全部完成了！\n" \
                                  f"一共获得 {self.today_have_get_coins} 个米游币\n目前有 {self.have_coins} 个米游币"
            log.info(f"今天已经全部完成了！一共获得 {self.today_have_get_coins} 个米游币，目前有 {self.have_coins} 个米游币")
            return return_data
        i = 0
        while self.today_get_coins != 0 and i < 2:
            if self.bbs_config["checkin"]:
                self.signing()
            self.get_tasks_list()
            i += 1
        return_data += "\n" + f"今天已经获得 {self.today_have_get_coins} 个米游币\n" \
                              f"还能获得 {self.today_get_coins} 个米游币\n目前有 {self.have_coins} 个米游币"
        log.info(f"今天已经获得 {self.today_have_get_coins} 个米游币，"
                 f"还能获得 {self.today_get_coins} 个米游币，目前有 {self.have_coins} 个米游币")
        wait()
        return return_data
