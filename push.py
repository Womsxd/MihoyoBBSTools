import os
from request import http
from configparser import ConfigParser

cfg = ConfigParser()


def load_config():
    config_path = os.path.dirname(os.path.realpath(__file__)) + "/push.ini"
    cfg.read(config_path)


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
    load_config()
    if cfg.getboolean('setting', 'enable'):
        if cfg.get('setting', 'push_server') == "cq_http":
            cq_http(status, push_message)
        elif cfg.get('setting', 'push_server') == "ftqq":
            ftqq(status, push_message)
        elif cfg.get('setting', 'push_server') == "pushplus":
            pushplus(status, push_message)
    return 0
