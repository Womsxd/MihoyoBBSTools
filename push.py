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


def ftqq(status, push_message):
    http.post(
        url="https://sctapi.ftqq.com/{}.send".format(cfg.get('setting', 'push_token')),
        data={
            "title": title(status),
            "desp": push_message
        }
    )


def pushplus(status, push_message):
    http.post(
        url="http://www.pushplus.plus/send",
        data={
            "token": cfg.get('setting', 'push_token'),
            "title": title(status),
            "content": push_message
        }
    )


def cq_http(status, push_message):
    http.post(
        url=cfg.get('cqhttp', 'cqhttp_url'),
        json={
            "user_id": cfg.getint('cqhttp', 'cqhttp_qq'),
            "message": title(status) + "\r\n" + push_message
        }
    )


def push(status, push_message):
    if not load_config():
        return 0
    if cfg.getboolean('setting', 'enable'):
        push_server = cfg.get('setting', 'push_server').lower()
        log.info("正在执行推送......")
        log.debug(f"推送所用的服务为：{push_server}")
        if push_server == "cqhttp":
            cq_http(status, push_message)
        elif push_server == "ftqq":
            ftqq(status, push_message)
        elif push_server == "pushplus":
            pushplus(status, push_message)
        log.info("推送完毕......")
    return 0
