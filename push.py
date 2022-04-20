import os
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
    else:
        return "「米游社脚本」执行失败!"


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
def cq_http(status, push_message):
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
    wechat_id = cfg.get('wecom', 'wechat_id')
    push_token = http.post(
        url=f'https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid={wechat_id}&corpsecret={secret}',
        data="").json()['access_token']
    push_data = {
        "agentid": cfg.get('wecom', 'agentid'),
        "msgtype": "text",
        "touser": "@all",
        "text": {
            "content": title(status) + "\r\n" + push_message
        }, "safe": 0}
    http.post(f'https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token={push_token}', json=push_data)


# pushdeer
def pushdeer(status, push_message):
    http.get(
        url=f'{cfg.get("pushdeer", "api_url")}/message/push',
        params={
            "push_key": cfg.get("pushdeer", "token"),
            "text": title(status),
            "desp": str(push_message).replace("\r\n", "\r\n\r\n"),
            "type": "markdown"
        }
    )


def push(status, push_message):
    if not load_config():
        return 0
    if cfg.getboolean('setting', 'enable'):
        push_server = cfg.get('setting', 'push_server').lower()
        log.info("正在执行推送......")
        try:
            log.debug(f"推送所用的服务为：{push_server}")
            eval(push_server[:10].lower() + "(status, push_message)")
        except NameError:
            log.warning("推送服务名称错误")
        else:
            log.info("推送完毕......")
    return 0
