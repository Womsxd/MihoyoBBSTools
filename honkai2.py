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
        self.headers = setting.headers
        self.headers['DS'] = tools.get_ds(web=True, web_old=True)
        self.headers['Referer'] = 'https://webstatic.mihoyo.com/bbs/event/signin/bh2/index.html?bbs_auth_required'\
                                  f'=true&act_id={setting.honkai2_Act_id}&bbs_presentation_style=fullscreen'\
                                  '&utm_source=bbs&utm_medium=mys&utm_campaign=icon'
        self.headers['Cookie'] = config.config["account"]["cookie"]
        self.headers['x-rpc-device_id'] = tools.get_device_id()
        self.acc_List = get_account_list("bh2_cn", self.headers)
        self.sign_day = 0
