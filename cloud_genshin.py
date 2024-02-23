import tools
import config
import setting
from request import http
from loghelper import log


class CloudGenshin:
    def __init__(self) -> None:
        self.headers = {
            'Host': 'api-cloudgame.mihoyo.com',
            'Accept': '*/*',
            'Referer': 'https://app.mihoyo.com',
            'x-rpc-combo_token': config.config['cloud_games']['genshin']['token'],
            'Accept-Encoding': 'gzip, deflate',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/99.0.4844.84 Safari/537.36',
        
        }

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
            ret_msg += f'你当前拥有免费时长 {tools.time_conversion(int(data["data"]["free_time"]["free_time"]))} ,' \
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
