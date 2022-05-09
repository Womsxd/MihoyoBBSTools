import os
import time
import base64
import hashlib
import urllib
import hmac
from request import http
from loghelper import log
from configparser import ConfigParser

cfg = ConfigParser()


def load_config():
    config_path = os.path.join(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'config'), 'push.ini')
    if os.path.exists(config_path):
        cfg.read(config_path, encoding='utf-8')
        return True
    else:
        return False


def title(status):
    if status == 0:
        return "「米游社脚本」执行成功!"
    elif status == 1:
        return "「米游社脚本」执行失败!"
    elif status == 2:
        return "「米游社脚本」部分账号执行失败！"


# telegram的推送
def telegram(status, push_message):
    http.post(
        url="https://{}/bot{}/sendMessage".format(cfg.get('telegram', 'api_url'), cfg.get('telegram', 'bot_token')),
        data={
            "chat_id": cfg.get('telegram', 'chat_id'),
            "text": title(status) + "\r\n" + push_message
        }
    )


# server酱
def ftqq(status, push_message):
    http.post(
        url="https://sctapi.ftqq.com/{}.send".format(cfg.get('setting', 'push_token')),
        data={
            "title": title(status),
            "desp": push_message
        }
    )


# pushplus
def pushplus(status, push_message):
    http.post(
        url="https://www.pushplus.plus/send",
        data={
            "token": cfg.get('setting', 'push_token'),
            "title": title(status),
            "content": push_message
        }
    )


# cq http协议的推送
def cqhttp(status, push_message):
    http.post(
        url=cfg.get('cqhttp', 'cqhttp_url'),
        json={
            "user_id": cfg.getint('cqhttp', 'cqhttp_qq'),
            "message": title(status) + "\r\n" + push_message
        }
    )


# 企业微信 感谢linjie5492@github
def wecom(status, push_message):
    secret = cfg.get('wecom', 'secret')
    corpid = cfg.get('wecom', 'wechat_id')
    try:
        touser = cfg.get('wecom', 'touser')
    except:
        # 没有配置时赋默认值
        touser = '@all'
    
    push_token = http.post(
        url=f'https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid={corpid}&corpsecret={secret}',
        data=""
    ).json()['access_token']
    push_data = {
        "agentid": cfg.get('wecom', 'agentid'),
        "msgtype": "text",
        "touser": touser,
        "text": {
            "content": title(status) + "\r\n" + push_message
        },
        "safe": 0
    }
    http.post(f'https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token={push_token}', json=push_data)


# pushdeer
def pushdeer(status, push_message):
    http.get(
        url=f'{cfg.get("pushdeer", "api_url")}/message/push',
        params={
            "pushkey": cfg.get("pushdeer", "token"),
            "text": title(status),
            "desp": str(push_message).replace("\r\n", "\r\n\r\n"),
            "type": "markdown"
        }
    )

# 钉钉群机器人
def dingrobot(status, push_message):
    api_url = cfg.get('dingrobot', 'webhook')  # https://oapi.dingtalk.com/robot/send?access_token=XXX
    secret = cfg.get('dingrobot', 'secret')    # 安全设置 -> 加签 -> 密钥 -> SEC*

    if secret:
        timestamp = str(round(time.time() * 1000))
        sign_string = f"{timestamp}\n{secret}"
        hmac_code = hmac.new(
            key=secret.encode("utf-8"),
            msg=sign_string.encode("utf-8"),
            digestmod=hashlib.sha256
        ).digest()
        sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))
        api_url = f"{api_url}&timestamp={timestamp}&sign={sign}"
    
    rep = http.post(
        url=api_url,
        headers={"Content-Type": "application/json; charset=utf-8"},
        json={
            "msgtype": "text", "text": { "content": title(status) + "\r\n" + push_message }
        }
    ).json()
    log.info(f"推送结果：{rep.get('errmsg')}")

# Bark
def bark(status, push_message):
    rep = http.get(
        url=f'{cfg.get("bark", "api_url")}/{cfg.get("bark", "token")}/{title(status)}/{push_message}'
    ).json()
    log.info(f"推送结果：{rep.get('message')}")

def push(status, push_message):
    if not load_config():
        return 0
    if cfg.getboolean('setting', 'enable'):
        log.info("正在执行推送......")
        func_name = cfg.get('setting', 'push_server').lower()
        func = globals().get(func_name)
        # print(func)
        if not func:
            log.warning("推送服务名称错误：请检查config/push.ini -> [setting] -> push_server")
            return 0
        log.debug(f"推送所用的服务为：{func_name}")
        try:
            # eval(push_server[:10] + "(status, push_message)")
            # 与面代码等效 20220508
            func(status, push_message)
        except Exception as r:
            log.warning(f"推送执行错误：{str(r)}")
            return 0
        else:
            log.info("推送完毕......")
    return 1

if __name__ == "__main__":
    push(0, f'推送验证{int(time.time())}')
