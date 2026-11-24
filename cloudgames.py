import random
import time
import logging

import tools
import config
import setting
from request import http
from loghelper import log


class CloudGameBase:
    def __init__(self, game_name, sign_url, coin_name, clear_cookie_func) -> None:
        self.headers = {}
        self.game_name = game_name
        self.sign_url = sign_url
        self.coin_name = coin_name
        self.clear_cookie_func = clear_cookie_func

    def sign_account(self) -> None:
        log.push(f"{self.game_name}：")

        try:
            req = http.get(url=self.sign_url, headers=self.headers)
            data = req.json()

            if data['retcode'] == 0:
                free_time_data = data["data"]["free_time"]
                free_time = int(free_time_data["free_time"])
                send_free_time = int(free_time_data["send_freetime"])

                if send_free_time > 0:
                    log.push(f'签到成功，已获得 {send_free_time} 分钟免费时长')
                elif free_time < 600:
                    time.sleep(random.randint(3, 6))
                    data2 = http.get(url=self.sign_url, headers=self.headers).json()
                    free_time2 = int(data2["data"]["free_time"]["free_time"])
                    if free_time2 > free_time:
                        log.push(f'签到成功，已获得 {free_time2 - free_time} 分钟免费时长')
                    else:
                        log.push('签到失败，未获得免费时长，可能是已经签到过了或者超出免费时长上限')
                log.push(f'你当前拥有免费时长 {tools.time_conversion(free_time)}，'
                         f'畅玩卡状态为 {data["data"]["play_card"]["short_msg"]}，'
                         f'拥有{self.coin_name} {data["data"]["coin"]["coin_num"]} 枚')
            elif data['retcode'] == -100:
                log.push("token 失效/防沉迷", level=logging.WARNING)
                self.clear_cookie_func()
            else:
                log.push(f'脚本签到失败，json 文本：{req.text}', level=logging.WARNING)
        except Exception as e:
            log.error(f'{self.game_name} 签到异常：{str(e)}')
            log.push('脚本签到发生异常，请查看日志', level=logging.WARNING)


class CloudGenshin(CloudGameBase):
    def __init__(self, token) -> None:
        super().__init__("云原神", setting.cloud_genshin_sgin, "米云币", config.clear_cookie_cloudgame_genshin)
        self.headers = {
            'Host': 'api-cloudgame.mihoyo.com',
            'Accept': '*/*',
            'Referer': 'https://app.mihoyo.com',
            'x-rpc-combo_token': token,
            'Accept-Encoding': 'gzip, deflate',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/99.0.4844.84 Safari/537.36',
        }


class CloudZZZ(CloudGameBase):
    def __init__(self, token) -> None:
        super().__init__("云绝区零", setting.cloud_zzz_sgin, "邦邦点", config.clear_cookie_cloudgame_zzz)
        self.headers = {
            'Host': 'cg-nap-api.mihoyo.com',
            'Accept': '*/*',
            'x-rpc-combo_token': token,
            'Accept-Encoding': 'gzip, deflate',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/99.0.4844.84 Safari/537.36',
        }


def run_task() -> None:
    cg_cn = config.config['cloud_games']['cn']
    if not cg_cn['enable']:
        return
    # 云原神签到
    if cg_cn['genshin']['enable'] and cg_cn['genshin']['token'] != "":
        CloudGenshin(cg_cn['genshin']['token']).sign_account()
    # 云绝区零签到
    if cg_cn['zzz']['enable'] and cg_cn['zzz']['token'] != "":
        CloudZZZ(cg_cn['zzz']['token']).sign_account()


if __name__ == '__main__':
    pass
