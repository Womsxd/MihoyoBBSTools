import time
import tools
import config
import random
import setting
from request import http
from loghelper import log
from account import get_account_list


class Honkai3rd:
    def __init__(self) -> None:
        self.headers = setting.headers
        self.headers['DS'] = tools.get_ds(web=True, web_old=True)
        self.headers['Referer'] = 'https://webstatic.mihoyo.com/bh3/event/euthenia/index.html?bbs_presentation_style' \
                                  '=fullscreen&bbs_game_role_required=bh3_cn&bbs_auth_required=true&act_id=' \
                                  f'{setting.honkai3rd_Act_id}&utm_source=bbs&utm_medium=mys&utm_campaign=icon'
        self.headers['Cookie'] = config.config["account"]["cookie"]
        self.headers['x-rpc-device_id'] = tools.get_device_id()
        self.account_list = get_account_list("bh3_cn", self.headers)
        self.sign_day = 0

    # 获取今天已经签到了的dict
    def get_today_item(self, raw_data: list):
        # 用range进行循环，当status等于0的时候上一个就是今天签到的dict
        for i in range(len(raw_data)):
            if raw_data[i]["status"] == 0:
                self.sign_day = i - 1
                return raw_data[i - 1]
            self.sign_day = i
            if raw_data[i]["status"] == 1:
                return raw_data[i]
            if i == int(len(raw_data) - 1) and raw_data[i]["status"] != 0:
                return raw_data[i]

    # 签到
    def sign_account(self) -> str:
        return_data = "崩坏3: "
        if len(self.account_list) == 0:
            log.warning("账号没有绑定任何崩坏3账号！")
            return_data += "\n并没有绑定任何崩坏3账号"
        else:
            for i in self.account_list:
                if i[1] in config.config["games"]["cn"]["honkai3rd"]["black_list"]:
                    continue
                log.info(f"正在为舰长 {i[0]} 进行签到...")
                req = http.get(setting.honkai3rd_Is_signurl.format(setting.honkai3rd_Act_id, i[2], i[1]),
                               headers=self.headers)
                data = req.json()
                re_message = ""
                if data["retcode"] != 0:
                    re_message = f"舰长 {i[0]} 获取账号签到信息失败！"
                    log.warning(re_message)
                    print(req.text)
                    continue
                today_item = self.get_today_item(data["data"]["sign"]["list"])
                # 判断是否已经签到
                if today_item["status"] == 0:
                    re_message = f"舰长 {i[0]} 今天已经签到过了~\t已连续签到{self.sign_day + 1}天\t今天获得的奖励是{tools.get_item(today_item)}"
                    log.info(re_message)
                else:
                    time.sleep(random.randint(2, 8))
                    req = http.post(url=setting.honkai3rd_SignUrl, headers=self.headers,
                                    json={'act_id': setting.honkai3rd_Act_id, 'region': i[2], 'uid': i[1]})
                    data = req.json()
                    if data["retcode"] == 0:
                        today_item = self.get_today_item(data["data"]["list"])
                        re_message = f"舰长 {i[0]} 签到成功~\t已连续签到{self.sign_day + 2}天\t今天获得的奖励是{tools.get_item(today_item)}"
                        log.info(re_message)
                    elif data["retcode"] == -5003:
                        re_message = f"舰长 {i[0]} 今天已经签到过了~\t已连续签到{self.sign_day + 1}天\t今天获得的奖励是{tools.get_item(today_item)}"
                        log.info(re_message)
                    else:
                        re_message = f"舰长 {i[0]} 本次签到失败！"
                        log.warning(re_message)
                        print(req.text)
                return_data += "\r\n" + re_message
        return return_data
