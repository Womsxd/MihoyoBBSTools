import time
import tools
import config
import random
import captcha
import setting
from error import *
from request import get_new_session
from loghelper import log

def wxmall_checkin()-> str:
    """
    :param wxmall_url: 微信商城url
    :param x_rpc_token: 用户token
    :return: 签到结果
    
    """
    http = get_new_session()

    x_rpc_token = config.config.get("wxmall", {}).get("token", "")

    headers = {
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
            'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 '
            'Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B) '
            'NetType/WIFI MiniProgramEnv/Windows WindowsWechat/WMPF '
            'WindowsWechat(0x63090719) XWEB/9129',
        "x-rpc-token": x_rpc_token ,
        "Referer": setting.wx_mall_referer_url,
        "xweb_xhr": "1"
    }
    
    return_data="微信商城签到结果\n"

    log.info("正在获取微信商城签到信息")
    req = http.get(setting.wx_mall_sign_task, headers=headers)
    data = req.json()
    if data["data"]["sign_today"]:
        log.info(f"今天已经签到过了~\r\n已经签到了{data['data']['sign_days']}天")
    else:
        time.sleep(random.randint(2, 8))
        log.info("今天还没有签到，开始签到")
        req = http.post(setting.wx_mall_sign, headers=headers, json={})
        data = req.json()
        if data["code"] == 0:
            log.info("签到成功")
        elif data["code"] == -522009:
            log.warning("请先手动绑定角色")
            return None
        else:
            if data["data"]["sign_today"]:
                log.info(f'签到成功~\r\n今天获得的奖励是{data["data"]["coin"]}积分')
                return_data= f'\n已经连续签到{data["data"]["continue_sign_days"]}天\r\n'\
                         f'累计签到{data["data"]["sign_days"]}天\r\n'
            else:
                log.warning(f'签到失败，错误信息：{data["msg"]}')
                return_data += "\n签到失败\n"
    return return_data

def run_task():
    ret_msg = ''
    ret_msg = wxmall_checkin()
    return ret_msg