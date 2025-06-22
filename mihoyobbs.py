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
            "sign": False,
            "read": False,
            "read_num": 3,
            "like": False,
            "like_num": 5,
            "share": False
        }
        self.get_tasks_list()
        # 如果这三个任务都做了就没必要获取帖子了
        if self.task_do["read"] and self.task_do["like"] and self.task_do["share"]:
            pass
        else:
            self.postsList = self.get_list()

    def refresh_list(self) -> None:
        self.postsList = self.get_list()

    def get_max_req_post_num(self):
        return max(self.task_do['read_num'], self.task_do['like_num'])

    def get_pass_challenge(self):
        req = http.get(url=setting.bbs_get_captcha, headers=self.headers)
        data = req.json()
        if data["retcode"] != 0:
            return None
        validate = captcha.bbs_captcha(data["data"]["gt"], data["data"]["challenge"])
        if validate is not None:
            check_req = http.post(url=setting.bbs_captcha_verify, headers=self.headers,
                                  json={"geetest_challenge": data["data"]["challenge"],
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
            59: {"attr": "read", "done": "is_get_award", "num_attr": "read_num"},
            60: {"attr": "like", "done": "is_get_award", "num_attr": "like_num"},
            61: {"attr": "share", "done": "is_get_award"}
        }
        if self.today_get_coins == 0:
            self.task_do["sign"] = True
            self.task_do["read"] = True
            self.task_do["like"] = True
            self.task_do["share"] = True
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
            new_day = data['data']['states'][0]['mission_id'] >= 62
            log.info(f"{'新的一天，今天可以获得' if new_day else '似乎还有任务没完成，今天还能获得'}"
                     f" {self.today_get_coins} 个米游币")

    # 获取要帖子列表
    def get_list(self) -> list:
        choice_post_list = []
        log.info("正在获取帖子列表......")
        req = http.get(url=setting.bbs_post_list_url,
                       params={"forum_id": self.bbs_list[0]["forumId"],
                               "is_good": str(False).lower(), "is_hot": str(False).lower(),
                               "page_size": 20, "sort_type": 1},
                       headers=self.headers)
        log.debug(req.text)
        data = req.json()["data"]["list"]
        while len(choice_post_list) < self.get_max_req_post_num():
            post = random.choice(data)
            if post["post"]["subject"] not in [x[1] for x in choice_post_list]:
                choice_post_list.append([post["post"]["post_id"], post["post"]["subject"]])
        log.info(f"已获取 {len(choice_post_list)} 个帖子")
        return choice_post_list

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

    # 看帖子
    def read_posts(self, post_info):
        req = http.get(url=setting.bbs_detail_url, params={"post_id": post_info[0]}, headers=self.headers)
        log.debug(req.text)
        data = req.json()
        if data["message"] == "OK":
            log.debug(f"看帖：{post_info[1]} 成功")

    # 点赞
    def like_posts(self, post_info, captcha_try: bool = False):
        header = deepcopy(self.headers)
        if captcha_try:
            challenge = self.get_pass_challenge()
            if challenge is not None:
                header["x-rpc-challenge"] = challenge
            else:
                # 验证码没通过
                wait()
        req = http.post(url=setting.bbs_like_url, headers=header,
                        json={"post_id": post_info[0], "is_cancel": False})
        log.debug(req.text)
        data = req.json()
        if data["message"] == "OK":
            log.debug("点赞：{} 成功".format(post_info[1]))
            # 判断取消点赞是否打开
            if self.bbs_config["cancel_like"]:
                wait()
                self.cancel_like_post(post_info)
            return True
        elif data["retcode"] == 1034 and not captcha_try:
            log.warning("点赞触发验证码")
            return self.like_posts(post_info, True)
        else:
            log.error(f"点赞失败：{req.text}")
        return False

    # 取消点赞
    def cancel_like_post(self, post_info):
        req = http.post(url=setting.bbs_like_url, headers=self.headers,
                        json={"post_id": post_info[0], "is_cancel": True})
        if req.json()["message"] == "OK":
            log.debug("取消点赞：{} 成功".format(post_info[1]))
            return True
        return False

    # 分享操作
    def share_post(self, post_info):
        for i in range(3):
            req = http.get(url=setting.bbs_share_url, params={"entity_id": post_info[0], "entity_type": 1},
                           headers=self.headers)
            log.debug(req.text)
            data = req.json()
            if data["message"] == "OK":
                log.debug(f"分享：{post_info[1]} 成功")
                break
            log.debug(f"分享任务执行失败，正在执行第 {i + 2} 次，共 3 次")
            wait()

    def post_task(self):
        log.info("正在执行帖子相关任务（看帖/点赞/分享）......")
        if self.task_do["read"] and self.task_do["like"] and self.task_do["share"]:
            log.info("帖子相关任务（看帖/点赞/分享）已全部完成!")
            return
        # 执行帖子的阅读 点赞 和 分享，其中阅读是必完成的
        for post in self.postsList:
            if self.bbs_config["read"] and not self.task_do["read"] and self.task_do["read_num"] > 0:
                self.read_posts(post)
                self.task_do["read_num"] -= 1
                wait()
            if self.bbs_config["like"] and not self.task_do["like"] and self.task_do["like_num"] > 0:
                self.like_posts(post)
                self.task_do["like_num"] -= 1
                wait()
            if self.bbs_config["share"] and not self.task_do["share"]:
                self.share_post(post)
                self.task_do["share"] = True
                wait()

    def run_task(self):
        return_data = "米游社: "
        if self.task_do["sign"] and self.task_do["read"] and self.task_do["like"] and \
                self.task_do["share"]:
            return_data += "\n" + f"今天已经全部完成了！\n" \
                                  f"一共获得 {self.today_have_get_coins} 个米游币\n目前有 {self.have_coins} 个米游币"
            log.info(f"今天已经全部完成了！一共获得 {self.today_have_get_coins} 个米游币，目前有 {self.have_coins} 个米游币")
            return return_data
        i = 0
        while self.today_get_coins != 0 and i < 2:
            if i > 0:
                wait()
                self.refresh_list()
            if self.bbs_config["checkin"]:
                self.signing()
            self.post_task()
            self.get_tasks_list()
            i += 1
        return_data += "\n" + f"今天已经获得 {self.today_have_get_coins} 个米游币\n" \
                              f"还能获得 {self.today_get_coins} 个米游币\n目前有 {self.have_coins} 个米游币"
        log.info(f"今天已经获得 {self.today_have_get_coins} 个米游币，"
                 f"还能获得 {self.today_get_coins} 个米游币，目前有 {self.have_coins} 个米游币")
        wait()
        return return_data
