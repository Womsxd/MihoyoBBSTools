import os
import hmac
import time
import base64
import config
import urllib
import hashlib
from datetime import datetime, timezone
from request import http, get_new_session_use_proxy
from loghelper import log
from configparser import ConfigParser, NoOptionError

cfg = ConfigParser()


def load_config():
    config_path = os.path.join(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'config'), 'push.ini')
    if os.path.exists(config_path):
        cfg.read(config_path, encoding='utf-8')
        return True
    else:
        return False


title = {
    0: "「米游社脚本」执行成功!",
    1: "「米游社脚本」执行失败!",
    2: "「米游社脚本」部分账号执行失败！",
    3: "「米游社脚本」游戏道具签到触发验证码！"
}


# telegram的推送
def telegram(send_title, push_message):
    http_proxy = cfg.get('telegram', 'http_proxy', fallback=None)
    if http_proxy:
        session = get_new_session_use_proxy(http_proxy)
    else:
        session = http
    session.post(
        url="https://{}/bot{}/sendMessage".format(cfg.get('telegram', 'api_url'), cfg.get('telegram', 'bot_token')),
        data={
            "chat_id": cfg.get('telegram', 'chat_id'),
            "text": send_title + "\r\n" + push_message
        }
    )


# server酱
def ftqq(send_title, push_message):
    http.post(
        url="https://sctapi.ftqq.com/{}.send".format(cfg.get('setting', 'push_token')),
        data={
            "title": send_title,
            "desp": push_message
        }
    )


# pushplus
def pushplus(send_title, push_message):
    http.post(
        url="https://www.pushplus.plus/send",
        data={
            "token": cfg.get('setting', 'push_token'),
            "title": send_title,
            "content": push_message
        }
    )


# cq http协议的推送
def cqhttp(send_title, push_message):
    http.post(
        url=cfg.get('cqhttp', 'cqhttp_url'),
        json={
            "user_id": cfg.getint('cqhttp', 'cqhttp_qq'),
            "message": send_title + "\r\n" + push_message
        }
    )


# smtp mail(电子邮件)
# 感谢 @islandwind 提供的随机壁纸api 个人主页：https://space.bilibili.com/7600422
def smtp(send_title, push_message):
    import smtplib
    from email.mime.text import MIMEText

    IMAGE_API = "https://api.iw233.cn/api.php?sort=random&type=json"

    try:
        image_url = http.get(IMAGE_API).json()["pic"][0]
    except:
        image_url = "unable to get the image"
        log.warning("获取随机背景图失败，请检查图片api")
    with open("assets/email_example.html", encoding="utf-8") as f:
        EMAIL_TEMPLATE = f.read()
    message = EMAIL_TEMPLATE.format(title=send_title, message=push_message.replace("\n", "<br/>"), image_url=image_url)
    message = MIMEText(message, "html", "utf-8")
    message['Subject'] = cfg["smtp"]["subject"]
    message['To'] = cfg["smtp"]["toaddr"]
    message['From'] = f"{cfg['smtp']['subject']}<{cfg['smtp']['fromaddr']}>"
    if cfg.getboolean("smtp", "ssl_enable"):
        server = smtplib.SMTP_SSL(cfg["smtp"]["mailhost"], cfg.getint("smtp", "port"))
    else:
        server = smtplib.SMTP(cfg["smtp"]["mailhost"], cfg.getint("smtp", "port"))
    server.login(cfg["smtp"]["username"], cfg["smtp"]["password"])
    server.sendmail(cfg["smtp"]["fromaddr"], cfg["smtp"]["toaddr"], message.as_string())
    server.close()
    log.info("邮件发送成功啦")


# 企业微信 感谢linjie5492@github
def wecom(send_title, push_message):
    secret = cfg.get('wecom', 'secret')
    corpid = cfg.get('wecom', 'wechat_id')
    try:
        touser = cfg.get('wecom', 'touser')
    except NoOptionError:
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
            "content": send_title + "\r\n" + push_message
        },
        "safe": 0
    }
    http.post(f'https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token={push_token}', json=push_data)


# 企业微信机器人
def wecomrobot(send_title, push_message):
    rep = http.post(
        url=f'{cfg.get("wecomrobot", "url")}',
        headers={"Content-Type": "application/json; charset=utf-8"},
        json={
            "msgtype": "text",
            "text": {
                "content": send_title + "\r\n" + push_message,
                "mentioned_mobile_list": [f'{cfg.get("wecomrobot", "mobile")}']
            }
        }
    ).json()
    log.info(f"推送结果：{rep.get('errmsg')}")


# pushdeer
def pushdeer(send_title, push_message):
    http.get(
        url=f'{cfg.get("pushdeer", "api_url")}/message/push',
        params={
            "pushkey": cfg.get("pushdeer", "token"),
            "text": send_title,
            "desp": str(push_message).replace("\r\n", "\r\n\r\n"),
            "type": "markdown"
        }
    )


# 钉钉群机器人
def dingrobot(send_title, push_message):
    api_url = cfg.get('dingrobot', 'webhook')  # https://oapi.dingtalk.com/robot/send?access_token=XXX
    secret = cfg.get('dingrobot', 'secret')  # 安全设置 -> 加签 -> 密钥 -> SEC*
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
            "msgtype": "text", "text": {"content": send_title + "\r\n" + push_message}
        }
    ).json()
    log.info(f"推送结果：{rep.get('errmsg')}")


# 飞书机器人
def feishubot(send_title, push_message):
    api_url = cfg.get('feishubot', 'webhook')  # https://open.feishu.cn/open-apis/bot/v2/hook/XXX
    rep = http.post(
        url=api_url,
        headers={"Content-Type": "application/json; charset=utf-8"},
        json={
            "msg_type": "text", "content": {"text": send_title + "\r\n" + push_message}
        }
    ).json()
    log.info(f"推送结果：{rep.get('msg')}")


# Bark
def bark(send_title, push_message):
    # make send_title and push_message to url encode
    send_title = urllib.parse.quote_plus(send_title)
    push_message = urllib.parse.quote_plus(push_message)
    rep = http.get(
        url=f'{cfg.get("bark", "api_url")}/{cfg.get("bark", "token")}/{send_title}/{push_message}?icon=https://cdn'
            f'.jsdelivr.net/gh/tanmx/pic@main/mihoyo/{cfg.get("bark", "icon")}.png'
    ).json()
    log.info(f"推送结果：{rep.get('message')}")


# gotify
def gotify(send_title, push_message):
    rep = http.post(
        url=f'{cfg.get("gotify", "api_url")}/message?token={cfg.get("gotify", "token")}',
        headers={"Content-Type": "application/json; charset=utf-8"},
        json={
            "title": send_title,
            "message": push_message,
            "priority": cfg.getint("gotify", "priority")
        }
    ).json()
    log.info(f"推送结果：{rep.get('errmsg')}")


# ifttt
def ifttt(send_title, push_message):
    ifttt_event = cfg.get('ifttt', 'event')
    ifttt_key = cfg.get('ifttt', 'key')
    rep = http.post(
        url=f'https://maker.ifttt.com/trigger/{ifttt_event}/with/key/{ifttt_key}',
        headers={"Content-Type": "application/json; charset=utf-8"},
        json={
            "value1": send_title,
            "value2": push_message
        }
    )
    if 'errors' in rep.text:
        log.warning(f"推送执行错误：{rep.json()['errors']}")
        return 0
    else:
        log.info("推送完毕......")
    return 1


# webhook
def webhook(send_title, push_message):
    rep = http.post(
        url=f'{cfg.get("webhook", "webhook_url")}',
        headers={"Content-Type": "application/json; charset=utf-8"},
        json={
            "title": send_title,
            "message": push_message
        }
    ).json()
    log.info(f"推送结果：{rep.get('errmsg')}")


# qmsg
def qmsg(send_title, push_message):
    rep = http.post(
        url=f'https://qmsg.zendee.cn/send/{cfg.get("qmsg", "key")}',
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data={
            "msg": send_title + "\n" + push_message
        }
    ).json()
    log.info(f"推送结果：{rep['reason']}")


def discord(send_title, push_message):
    import pytz
    
    rep = http.post(
        url=f'{cfg.get("discord", "webhook")}',
        headers={"Content-Type": "application/json; charset=utf-8"},
        json={
              "content": None,
              "embeds": [
                {
                  "title": send_title,
                  "description": push_message,
                  "color": 1926125,
                  "author": {
                    "name": "MihoyoBBSTools",
                    "url": "https://github.com/Womsxd/MihoyoBBSTools",
                    "icon_url": "https://github.com/DGP-Studio/Snap.Hutao.Docs/blob/main/docs/.vuepress/public/images/202308/hoyolab-miyoushe-Icon.png?raw=true"
                  },
                  "timestamp": datetime.now(timezone.utc).astimezone(pytz.timezone('Asia/Shanghai')).isoformat()
                }
              ],
            "username": "MihoyoBBSTools",
            "avatar_url": "https://github.com/DGP-Studio/Snap.Hutao.Docs/blob/main/docs/.vuepress/public/images/202308/hoyolab-miyoushe-Icon.png?raw=true",
            "attachments": []
            }
    )
    if rep.status_code != 204:
        log.warning(f"推送执行错误：{rep.text}")
    else:
        log.info(f"推送结果：HTTP {rep.status_code} Success")

def wintoast(send_title, push_message):
    try:
        from win11toast import toast
        toast(app_id="MihoyoBBSTools",title=send_title,body=push_message,icon='')
    except:
        log.error(f"请先pip install win11toast再使用win通知")
    


def push(status, push_message):
    if not load_config():
        return 1
    if not cfg.getboolean('setting', 'enable'):
        return 0
    log.info("正在执行推送......")
    func_names = cfg.get('setting', 'push_server').lower()
    for func_name in func_names.split(","):
        func = globals().get(func_name)
        if not func:
            log.warning("推送服务名称错误：请检查config/push.ini -> [setting] -> push_server")
            continue
        log.debug(f"推送所用的服务为: {func_name}")
        try:
            if not config.update_config_need:
                func(title.get(status, ''), push_message)
            else:
                func('「米游社脚本」config可能需要手动更新',
                     f'如果您多次收到此消息开头的推送，证明您运行的环境无法自动更新config，请手动更新一下，谢谢\r\n'
                     f'{title.get(status, "")}\r\n{push_message}')
        except Exception as r:
            log.warning(f"推送执行错误：{str(r)}")
            return 1
        log.info(f"{func_name} - 推送完毕......")
    return 0


if __name__ == "__main__":
    push(0, f'推送验证{int(time.time())}')
