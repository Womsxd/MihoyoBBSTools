import tools
import config
import setting
from loghelper import log
from request import get_new_session


class CloudGenshin:
    def __init__(self, token, lang) -> None:
        self.http = get_new_session()
        self.headers = {
            'Accept': '*/*',
            'x-rpc-combo_token': token,
            'Accept-Encoding': 'gzip, deflate',
            'User-Agent': 'okhttp/4.10.0',
            'x-rpc-client_type': 3,
            'x-rpc-cg_game_biz': 'hk4e_global',
            'x-rpc-channel_id': 1,
            'x-rpc-language': lang

        }

    def sign_account(self) -> str:
        ret_msg = "云原神:\r\n"
        req = self.http.get(url=setting.cloud_genshin_sgin_os, headers=self.headers)
        data = req.json()
        if data['retcode'] == 0:
            if int(data["data"]["free_time"]["send_freetime"]) > 0:
                log.info(f'签到成功，已获得 {data["data"]["free_time"]["send_freetime"]} 分钟免费时长')
                ret_msg += f'签到成功，已获得 {data["data"]["free_time"]["send_freetime"]} 分钟免费时长\n'
            else:
                log.info('签到失败，未获得免费时长，可能是已经签到过了或者超出免费时长上限')
                ret_msg += '签到失败，未获得免费时长，可能是已经签到过了或者超出免费时长上限\n'
            ret_msg += f'你当前拥有免费时长 {tools.time_conversion(int(data["data"]["free_time"]["free_time"]))}，' \
                       f'畅玩卡状态为 {data["data"]["play_card"]["short_msg"]}，拥有米云币 {data["data"]["coin"]["coin_num"]} 枚'
            log.info(ret_msg)
        elif data['retcode'] == -100:
            ret_msg = "云原神 token 失效"
            log.warning(ret_msg)
            config.clear_cookie_cloudgame_genshin_os()
        else:
            ret_msg = f'脚本签到失败，json 文本：{req.text}'
            log.warning(ret_msg)
        return ret_msg


def run_task() -> str:
    ret_msg = ""
    cg_os = config.config['cloud_games']['os']
    if not cg_os['genshin']['enable'] or cg_os['genshin']['token'] == "":
        return ""
    cg_genshin = CloudGenshin(cg_os['genshin']['token'], cg_os['lang'])
    ret_msg += cg_genshin.sign_account() + "\n\n"
    return ret_msg
