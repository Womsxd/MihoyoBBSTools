import time
import tools
import config
import random
import setting
from request import http
from loghelper import log
from error import CookieError
from account import get_account_list


class Honkai2:
    def __init__(self) -> None:
        self.headers = {
            'Accept': 'application/json, text/plain, */*',
            'DS': tools.get_ds(web=True, web_old=True),
            'Origin': 'https://webstatic.mihoyo.com',
            'x-rpc-app_version': setting.mihoyobbs_Version_old,
            'User-Agent': 'Mozilla/5.0 (Linux; Android 9; Unspecified Device) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Version/4.0 Chrome/39.0.0.0 Mobile Safari/537.36 miHoYoBBS/2.3.0',
            'x-rpc-client_type': setting.mihoyobbs_Client_type_web,
            'Referer': 'https://webstatic.mihoyo.com/bbs/event/signin/bh2/index.html?bbs_auth_required=true&'
                       f'act_id={setting.honkai2_Act_id}&bbs_presentation_style=fullscreen&utm_source=bbs&'
                       'utm_medium=mys&utm_campaign=icon',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,en-US;q=0.8',
            'X-Requested-With': 'com.mihoyo.hyperion',
            "Cookie": config.cookies,
            'x-rpc-device_id': tools.get_device_id()
        }
        self.acc_List = get_account_list("bh2_cn", self.headers)
        self.sign_day = 0
