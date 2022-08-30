import json
import tools
import config
import setting
from request import http
from loghelper import log


class CloudGenshin:
    def __init__(self) -> None:
        self.headers = {
            'x-rpc-combo_token': config.config['cloud_games']['genshin']['token'],
            'x-rpc-client_type': setting.mihoyobbs_Client_type,
            'x-rpc-app_version': setting.cloudgenshin_Version,
            'x-rpc-sys_version': '12',
            'x-rpc-channel': 'mihoyo',
            'x-rpc-device_id': tools.get_device_id(),
            'x-rpc-device_name': 'Xiaomi M2012K11AC',
            'x-rpc-device_model': 'M2012K11AC',
            'x-rpc-app_id': '1953439974',
            'Referer': 'https://app.mihoyo.com',
            'Host': 'api-cloudgame.mihoyo.com',
            'Connection': 'Keep-Alive',
            'Accept-Encoding': 'gzip',
            'User-Agent': 'okhttp/4.9.0'
        }

    # 分钟转小时
    def Time_Conversion(self,minute : int) -> str:
        h = minute//60
        s = minute%60
        return f"{h}小时{s}分钟"

    def sign_account(self) -> str:
        ret_msg = "云原神:\r\n"
        req = http.get(url=setting.cloud_genshin_sgin, headers=self.headers)
        data = req.json()
        if data['retcode'] == 0:
            if int(data["data"]["free_time"]["send_freetime"]) > 0:
                log.info(f'签到成功，已获得{data["data"]["free_time"]["send_freetime"]}分钟免费时长')
                ret_msg += f'签到成功，已获得{data["data"]["free_time"]["send_freetime"]}分钟免费时长\n'
            else:
                log.info('签到失败，未获得免费时长，可能是已经签到过了或者超出免费时长上线')
                ret_msg += '签到失败，未获得免费时长，可能是已经签到过了或者超出免费时长上线\n'
            ret_msg += f'你当前拥有免费时长 {self.Time_Conversion(int(data["data"]["free_time"]["free_time"]))} ,' \
                      f'畅玩卡状态为 {data["data"]["play_card"]["short_msg"]}，拥有米云币 {data["data"]["coin"]["coin_num"]} 枚'
            log.info(ret_msg)
        elif data['retcode'] == -100:
            ret_msg = "云原神token失效/防沉迷"
            log.warning(ret_msg)
            config.clear_cookie_cloudgame()
        else:
            ret_msg = f'脚本签到失败，json文本:{req.text}'
            log.warning(ret_msg)
        return ret_msg


if __name__ == '__main__':
    pass
