import time
import tools
import config
import random
import setting
from request import http
from loghelper import log
from error import CookieError


class Genshin:
    def __init__(self) -> None:
        self.headers = {
            'Accept': 'application/json, text/plain, */*',
            'DS': tools.get_ds(web=True, web_old=True),
            'Origin': 'https://webstatic.mihoyo.com',
            'x-rpc-app_version': setting.mihoyobbs_Version_old,
            'User-Agent': 'Mozilla/5.0 (Linux; Android 9; Unspecified Device) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/39.0.0.0 Mobile Safari/537.36 miHoYoBBS/2.3.0',
            'x-rpc-client_type': setting.mihoyobbs_Client_type_web,
            'Referer': 'https://webstatic.mihoyo.com/bbs/event/signin-ys/index.html?bbs_auth_required=true&act_id=e202009291139501&utm_source=bbs&utm_medium=mys&utm_campaign=icon',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,en-US;q=0.8',
            'X-Requested-With': 'com.mihoyo.hyperion',
            "Cookie": config.mihoyobbs_Cookies,
            'x-rpc-device_id': tools.get_device_id()
        }
        self.acc_List = self.get_account_list()
        if len(self.acc_List) != 0:
            self.sign_Give = self.get_signgive()

    # 获取绑定的账号列表
    def get_account_list(self) -> list:
        log.info("正在获取米哈游账号绑定原神账号列表...")
        temp_list = []
        req = http.get(setting.genshin_Account_info_url, headers=self.headers)
        data = req.json()
        if data["retcode"] != 0:
            log.warning("获取账号列表失败！")
            config.genshin_Auto_sign = False
            config.save_config()
            raise CookieError("BBS Cookie Errror")
        for i in data["data"]["list"]:
            temp_list.append([i["nickname"], i["game_uid"], i["region"]])
        log.info(f"已获取到{len(temp_list)}个原神账号信息")
        return temp_list

    # 获取已经签到奖励列表
    def get_signgive(self) -> list:
        log.info("正在获取签到奖励列表...")
        req = http.get(setting.genshin_Signlisturl.format(setting.genshin_Act_id), headers=self.headers)
        data = req.json()
        if data["retcode"] != 0:
            log.warning("获取签到奖励列表失败")
            print(req.text)
        return data["data"]["awards"]

    # 判断签到
    def is_sign(self, region: str, uid: str):
        req = http.get(setting.genshin_Is_signurl.format(setting.genshin_Act_id, region, uid), headers=self.headers)
        data = req.json()
        if data["retcode"] != 0:
            log.warning("获取账号签到信息失败！")
            print(req.text)
            config.genshin_Auto_sign = False
            config.save_config()
            raise CookieError("BBS Cookie Errror")
        return data["data"]

    # 签到
    def sign_account(self):
        return_data = "原神："
        if len(self.acc_List) != 0:
            for i in self.acc_List:
                log.info(f"正在为旅行者{i[0]}进行签到...")
                time.sleep(random.randint(2, 8))
                is_data = self.is_sign(region=i[2], uid=i[1])
                if is_data["first_bind"]:
                    log.warning(f"旅行者{i[0]}是第一次绑定米游社，请先手动签到一次")
                else:
                    sign_days = is_data["total_sign_day"] - 1
                    if is_data["is_sign"]:
                        log.info(f"旅行者{i[0]}今天已经签到过了~\r\n今天获得的奖励是{tools.get_item(self.sign_Give[sign_days])}")
                    else:
                        time.sleep(random.randint(2, 8))
                        req = http.post(url=setting.genshin_Signurl, headers=self.headers,
                                        json={'act_id': setting.genshin_Act_id, 'region': i[2], 'uid': i[1]})
                        data = req.json()
                        if data["retcode"] == 0:
                            if sign_days == 0:
                                log.info(f"旅行者{i[0]}签到成功~\r\n今天获得的奖励是{tools.get_item(self.sign_Give[sign_days])}")
                            else:
                                log.info(
                                    f"旅行者{i[0]}签到成功~\r\n今天获得的奖励是{tools.get_item(self.sign_Give[sign_days + 1])}")
                        elif data["retcode"] == -5003:
                            log.info(f"旅行者{i[0]}今天已经签到过了~\r\n今天获得的奖励是{tools.get_item(self.sign_Give[sign_days])}")
                        else:
                            log.warning("账号签到失败！")
                            print(req.text)
                    if is_data["is_sign"] or data["retcode"] == 0 or data["retcode"] == -5003:
                        return_data += f"\n{i[0]}已连续签到{sign_days}天\n今天获得的奖励是{tools.get_item(self.sign_Give[sign_days])}"
                    else:
                        return_data += f"\n{i[0]}，本次签到失败"
        else:
            log.warning("账号没有绑定任何原神账号！")
            return_data += "\n并没有绑定任何原神账号"
        return return_data
