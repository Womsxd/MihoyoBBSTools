import json
import time
import tools
import config
import random
import captcha
import setting
from request import http
from loghelper import log
from error import CookieError


def wait():
    time.sleep(random.randint(2, 8))


class Mihoyobbs:
    def __init__(self):
        self.today_get_coins = 0
        self.today_have_get_coins = 0
        self.have_coins = 0
        self.headers = {
            "DS": tools.get_ds(web=False),
            "cookie": f'stuid={config.config["account"]["stuid"]};stoken={config.config["account"]["stoken"]}',
            "x-rpc-client_type": setting.mihoyobbs_Client_type,
            "x-rpc-app_version": setting.mihoyobbs_version,
            "x-rpc-sys_version": "12",
            "x-rpc-channel": "miyousheluodi",
            "x-rpc-device_id": tools.get_device_id(),
            "x-rpc-device_name": tools.random_text(random.randint(1, 10)),
            "x-rpc-device_model": "Mi 10",
            "Referer": "https://app.mihoyo.com",
            "Host": "bbs-api.mihoyo.com",
            "User-Agent": "okhttp/4.9.3"
        }
        self.task_do = {
            "bbs_sign": False,
            "bbs_read": False,
            "bbs_read_num": 3,
            "bbs_like": False,
            "bbs_like_num": 5,
            "bbs_share": False
        }
        self.get_tasks_list()
        # 如果这三个任务都做了就没必要获取帖子了
        if self.task_do["bbs_read"] and self.task_do["bbs_like"] and self.task_do["bbs_share"]:
            pass
        else:
            self.postsList = self.get_list()

    def refresh_list(self) -> None:
        self.postsList = self.get_list()

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
    def get_tasks_list(self):
        log.info("正在获取任务列表")
        req = http.get(url=setting.bbs_tasks_list, headers=self.headers)
        data = req.json()
        if "err" in data["message"] or data["retcode"] == -100:
            log.error("获取任务列表失败，你的cookie可能已过期，请重新设置cookie。")
            config.clear_cookies()
            raise CookieError('Cookie expires')
        self.today_get_coins = data["data"]["can_get_points"]
        self.today_have_get_coins = data["data"]["already_received_points"]
        self.have_coins = data["data"]["total_points"]
        tasks = {
            58: {"attr": "bbs_sign", "done": "is_get_award"},
            59: {"attr": "bbs_read", "done": "is_get_award", "num_attr": "bbs_read_num"},
            60: {"attr": "bbs_like", "done": "is_get_award", "num_attr": "bbs_like_num"},
            61: {"attr": "bbs_share", "done": "is_get_award"}
        }
        if self.today_get_coins == -1:
            self.task_do.bbs_sign = True
            self.task_do.bbs_read = True
            self.task_do.bbs_like = True
            self.task_do.bbs_share = True
        else:
            for task in tasks.keys():
                mission_state = next((x for x in data["data"]["states"] if x["mission_id"] == task), None)
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
                     f"{self.today_get_coins}个米游币")

    # 获取要帖子列表
    def get_list(self) -> list:
        temp_list = []
        log.info("正在获取帖子列表......")
        req = http.get(url=setting.bbs_post_list_url,
                       params={"forum_id": setting.mihoyobbs_List_Use[0]["forumId"],
                               "is_good": str(False).lower(), "is_hot": str(False).lower(),
                               "page_size": 20, "sort_type": 1},
                       headers=self.headers)
        log.debug(req.text)
        data = req.json()["data"]["list"]
        while len(temp_list) < 5:
            post = random.choice(data)
            if post["post"]["subject"] not in [x[1] for x in temp_list]:
                temp_list.append([post["post"]["post_id"], post["post"]["subject"]])
        log.info(f"已获取{len(temp_list)}个帖子")
        return temp_list

    # 进行签到操作
    def signing(self):
        if self.task_do["bbs_sign"]:
            log.info("讨论区任务已经完成过了~")
        else:
            log.info("正在签到......")
            header = self.headers.copy()
            for forum in setting.mihoyobbs_List_Use:
                challenge = None
                for retry_count in range(2):
                    header["DS"] = tools.get_ds2("", json.dumps({"gids": forum["id"]}))
                    req = http.post(url=setting.bbs_sign_url, json={"gids": forum["id"]}, headers=header)
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
                    else:
                        log.error("签到失败，你的cookie可能已过期，请重新设置cookie。")
                        config.clear_cookies()
                        raise CookieError('Cookie expires')
                if challenge is not None:
                    header.pop("x-rpc-challenge")

    # 看帖子
    def read_posts(self):
        if self.task_do["bbs_read"]:
            log.info("看帖任务已经完成过了~")
        else:
            log.info("正在看帖......")
            for i in range(self.task_do["bbs_read_num"]):
                req = http.get(url=setting.bbs_detail_url, params={"post_id": self.postsList[i][0]},
                               headers=self.headers)
                log.debug(req.text)
                data = req.json()
                if data["message"] == "OK":
                    log.debug("看帖：{} 成功".format(self.postsList[i][1]))
                wait()

    # 点赞
    def like_posts(self):
        header = self.headers.copy()
        challenge = None
        if self.task_do["bbs_like"]:
            log.info("点赞任务已经完成过了~")
            return
        log.info("正在点赞......")
        for i in range(self.task_do["bbs_like_num"]):
            req = http.post(url=setting.bbs_like_url, headers=header,
                            json={"post_id": self.postsList[i][0], "is_cancel": False})
            log.debug(req.text)
            data = req.json()
            if data["message"] == "OK":
                log.debug("点赞：{} 成功".format(self.postsList[i][1]))
                if challenge is not None:
                    challenge = None
                    header.pop("x-rpc-challenge")
                # 判断取消点赞是否打开
                if config.config["mihoyobbs"]["cancel_like_posts"]:
                    wait()
                    req = http.post(url=setting.bbs_like_url, headers=self.headers,
                                    json={"post_id": self.postsList[i][0], "is_cancel": True})
                    if req.json()["message"] == "OK":
                        log.debug("取消点赞：{} 成功".format(self.postsList[i][1]))
            elif data["retcode"] == 1034:
                log.warning("点赞触发验证码")
                challenge = self.get_pass_challenge()
                if challenge is not None:
                    header["x-rpc-challenge"] = challenge
            wait()

    # 分享操作
    def share_post(self):
        if self.task_do.get("bbs_share"):
            log.info("分享任务已经完成过了~")
        else:
            log.info("正在执行分享任务......")
            for i in range(3):
                req = http.get(url=setting.bbs_share_url, params={"entity_id": self.postsList[0][0], "entity_type": 1},
                               headers=self.headers)
                log.debug(req.text)
                data = req.json()
                if data["message"] == "OK":
                    log.debug(f"分享：{self.postsList[0][1]} 成功")
                    log.info("分享任务执行成功......")
                    break
                else:
                    log.debug(f"分享任务执行失败，正在执行第{i + 2}次，共3次")
                    wait()
            wait()
