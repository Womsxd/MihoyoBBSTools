import os
import re
import hmac
import time
import base64
import config
import urllib
import hashlib
from datetime import datetime, timezone
from request import get_new_session, get_new_session_use_proxy
from loghelper import log
from configparser import ConfigParser, NoOptionError

title = {
    -99: "「米游社脚本」依赖缺失",
    -2: "「米游社脚本」StatusID 错误",
    -1: "「米游社脚本」Config版本已更新",
    0: "「米游社脚本」执行成功!",
    1: "「米游社脚本」执行失败!",
    2: "「米游社脚本」部分账号执行失败！",
    3: "「米游社脚本」社区/游戏道具签到触发验证码！"
}


def get_push_title(status_id) -> str:
    """
    获取推送标题
    :param status_id: 状态ID
    :return:
    """
    return title.get(status_id, title.get(-2))


class PushHandler:
    def __init__(self, config_file="push.ini"):
        self.http = get_new_session()
        self.cfg = ConfigParser()
        self.config_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'config')
        self.config_name = config_file

    def get_config_path(self):
        file_path = self.config_path
        file_name = self.config_name
        if os.getenv("AutoMihoyoBBS_push_path"):
            file_path = os.getenv("AutoMihoyoBBS_push_path")
        if os.getenv("AutoMihoyoBBS_push_name"):
            file_name = os.getenv("AutoMihoyoBBS_push_name")
        return os.path.join(file_path, file_name)

    def load_config(self):
        file_path = self.get_config_path()
        if os.path.exists(file_path):
            self.cfg.read(file_path, encoding='utf-8')
            return True
        else:
            if self.config_name != "push.ini":
                log.warning(f"配置文件 {file_path} 不存在！")
            return False

    # 推送消息中屏蔽关键词
    def msg_replace(self, msg):
        block_keys = []
        try:
            block_str = self.cfg.get('setting', 'push_block_keys')
            block_keys = block_str.split(',')
        except:
            return msg
        else:
            for block_key in block_keys:
                block_key_trim = str(block_key).strip()
                if block_key_trim:
                    msg = str(msg).replace(block_key_trim, "*" * len(block_key_trim))
            return msg

    def telegram(self, status_id, push_message):
        http_proxy = self.cfg.get('telegram', 'http_proxy', fallback=None)
        session = get_new_session_use_proxy(http_proxy) if http_proxy else self.http
        session.post(
            url=f"https://{self.cfg.get('telegram', 'api_url')}/bot{self.cfg.get('telegram', 'bot_token')}/sendMessage",
            data={
                "chat_id": self.cfg.get('telegram', 'chat_id'),
                "text": get_push_title(status_id) + "\r\n" + push_message
            }
        )

    def ftqq(self, status_id, push_message):
        """
        Server酱推送，具体推送位置在server酱后台配置
        """
        self.http.post(
            url="https://sctapi.ftqq.com/{}.send".format(self.cfg.get('setting', 'push_token')),
            data={
                "title": get_push_title(status_id),
                "desp": push_message
            }
        )

    def pushplus(self, status_id, push_message):
        """
        PushPlus推送
        """
        self.http.post(
            url="https://www.pushplus.plus/send",
            data={
                "token": self.cfg.get('setting', 'push_token'),
                "title": get_push_title(status_id),
                "content": push_message,
                "topic": self.cfg.get('setting', 'topic')
            }
        )

    def pushme(self, status_id, push_message):
        """
        PushMe推送
        """
        pushme_key = self.cfg.get('pushme', 'token')
        if not pushme_key:
            log.error("PushMe 推送失败！PUSHME_KEY 未设置")
            return
        log.info("PushMe 服务启动")
        data = {
            "push_key": pushme_key,
            "title": get_push_title(status_id),
            "content": push_message,
            "date": "",
            "type": ""
        }
        log.debug(f"PushMe 请求数据: {data}")
        response = self.http.post(
            url=self.cfg.get('pushme', 'url', fallback="https://push.i-i.me/"),
            data=data)
        log.debug(f"PushMe 响应状态码: {response.status_code}")
        log.debug(f"PushMe 响应内容: {response.text}")
        if response.status_code == 200 and response.text == "success":
            log.info("PushMe 推送成功！")
        else:
            log.error(f"PushMe 推送失败！{response.status_code} {response.text}")

    def cqhttp(self, status_id, push_message):
        """
        OneBot V11(CqHttp)协议推送
        """
        self.http.post(
            url=self.cfg.get('cqhttp', 'cqhttp_url'),
            json={
                "user_id": self.cfg.getint('cqhttp', 'cqhttp_qq'),
                "message": get_push_title(status_id) + "\r\n" + push_message
            }
        )

    # 感谢 @islandwind 提供的随机壁纸api 个人主页：https://space.bilibili.com/7600422
    def smtp(self, status_id, push_message):
        """
        SMTP 电子邮件推送
        """
        import smtplib
        from email.mime.text import MIMEText

        def get_background_url():
            try:
                _image_url = self.http.get("https://api.iw233.cn/api.php?sort=random&type=json").json()["pic"][0]
            except:
                _image_url = "unable to get the image"
                log.warning("获取随机背景图失败，请检查图片 api")
            return _image_url

        def get_background_img_html(background_url):
            if background_url:
                return f'<img src="{background_url}" alt="background" style="width: 100%; filter: brightness(50%)">'
            return ""

        def get_background_img_info(background_url):
            if background_url:
                return f'<p style="color: #fff;text-shadow:0px 0px 10px #000;">背景图片链接</p>\n' \
                       f'<a href="{background_url}" style="color: #fff;text-shadow:0px 0px 10px #000;">{background_url}</a>'
            return ""

        image_url = None
        if self.cfg.getboolean('smtp', 'background', fallback=True):
            image_url = get_background_url()

        with open("assets/email_example.html", encoding="utf-8") as f:
            EMAIL_TEMPLATE = f.read()
        message = EMAIL_TEMPLATE.format(title=get_push_title(status_id), message=push_message.replace("\n", "<br/>"),
                                        background_image=get_background_img_html(image_url),
                                        background_info=get_background_img_info(image_url))
        smtp_info = self.cfg["smtp"]
        message = MIMEText(message, "html", "utf-8")
        message['Subject'] = smtp_info["subject"]
        message['To'] = smtp_info["toaddr"]
        message['From'] = f"{smtp_info['subject']}<{smtp_info['fromaddr']}>"
        if self.cfg.getboolean("smtp", "ssl_enable"):
            server = smtplib.SMTP_SSL(smtp_info["mailhost"], self.cfg.getint("smtp", "port"))
        else:
            server = smtplib.SMTP(smtp_info["mailhost"], self.cfg.getint("smtp", "port"))
        server.login(smtp_info["username"], smtp_info["password"])
        server.sendmail(smtp_info["fromaddr"], smtp_info["toaddr"], message.as_string())
        server.close()
        log.info("邮件发送成功啦")

    def wecom(self, status_id, push_message):
        """
        企业微信推送
        感谢linjie5493@github 提供的代码
        """
        secret = self.cfg.get('wecom', 'secret')
        corpid = self.cfg.get('wecom', 'wechat_id')
        try:
            touser = self.cfg.get('wecom', 'touser')
        except NoOptionError:
            # 没有配置时赋默认值
            touser = '@all'

        push_token = self.http.post(
            url=f'https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid={corpid}&corpsecret={secret}',
            data=""
        ).json()['access_token']
        push_data = {
            "agentid": self.cfg.get('wecom', 'agentid'),
            "msgtype": "text",
            "touser": touser,
            "text": {
                "content": get_push_title(status_id) + "\r\n" + push_message
            },
            "safe": 0
        }
        self.http.post(f'https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token={push_token}', json=push_data)

    def wecomrobot(self, status_id, push_message):
        """
        企业微信机器人
        """
        rep = self.http.post(
            url=f'{self.cfg.get("wecomrobot", "url")}',
            headers={"Content-Type": "application/json; charset=utf-8"},
            json={
                "msgtype": "text",
                "text": {
                    "content": get_push_title(status_id) + "\r\n" + push_message,
                    "mentioned_mobile_list": [f'{self.cfg.get("wecomrobot", "mobile")}']
                }
            }
        ).json()
        log.info(f"推送结果：{rep.get('errmsg')}")

    def pushdeer(self, status_id, push_message):
        """
        PushDeer推送
        """
        self.http.get(
            url=f'{self.cfg.get("pushdeer", "api_url")}/message/push',
            params={
                "pushkey": self.cfg.get("pushdeer", "token"),
                "text": get_push_title(status_id),
                "desp": str(push_message).replace("\r\n", "\r\n\r\n"),
                "type": "markdown"
            }
        )

    def dingrobot(self, status_id, push_message):
        """
        钉钉群机器人推送
        """
        api_url = self.cfg.get('dingrobot', 'webhook')  # https://oapi.dingtalk.com/robot/send?access_token=XXX
        secret = self.cfg.get('dingrobot', 'secret')  # 安全设置 -> 加签 -> 密钥 -> SEC*
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

        rep = self.http.post(
            url=api_url,
            headers={"Content-Type": "application/json; charset=utf-8"},
            json={
                "msgtype": "text", "text": {"content": get_push_title(status_id) + "\r\n" + push_message}
            }
        ).json()
        log.info(f"推送结果：{rep.get('errmsg')}")

    def feishubot(self, status_id, push_message):
        """
        飞书机器人(WebHook)
        """
        api_url = self.cfg.get('feishubot', 'webhook')  # https://open.feishu.cn/open-apis/bot/v2/hook/XXX
        rep = self.http.post(
            url=api_url,
            headers={"Content-Type": "application/json; charset=utf-8"},
            json={
                "msg_type": "text", "content": {"text": get_push_title(status_id) + "\r\n" + push_message}
            }
        ).json()
        log.info(f"推送结果：{rep.get('msg')}")

    def bark(self, status_id, push_message):
        """
        Bark推送
        """
        # make send_title and push_message to url encode
        send_title = urllib.parse.quote_plus(get_push_title(status_id))
        push_message = urllib.parse.quote_plus(push_message)
        rep = self.http.get(
            url=f'{self.cfg.get("bark", "api_url")}/{self.cfg.get("bark", "token")}/{send_title}/{push_message}?'
                f'icon=https://cdn.jsdelivr.net/gh/tanmx/pic@main/mihoyo/{self.cfg.get("bark", "icon")}.png'
        ).json()
        log.info(f"推送结果：{rep.get('message')}")

    def gotify(self, status_id, push_message):
        """
        gotify
        """
        rep = self.http.post(
            url=f'{self.cfg.get("gotify", "api_url")}/message?token={self.cfg.get("gotify", "token")}',
            headers={"Content-Type": "application/json; charset=utf-8"},
            json={
                "title": get_push_title(status_id),
                "message": push_message,
                "priority": self.cfg.getint("gotify", "priority")
            }
        ).json()
        log.info(f"推送结果：{rep.get('errmsg')}")

    def ifttt(self, status_id, push_message):
        """
        ifttt
        """
        ifttt_event = self.cfg.get('ifttt', 'event')
        ifttt_key = self.cfg.get('ifttt', 'key')
        rep = self.http.post(
            url=f'https://maker.ifttt.com/trigger/{ifttt_event}/with/key/{ifttt_key}',
            headers={"Content-Type": "application/json; charset=utf-8"},
            json={
                "value1": get_push_title(status_id),
                "value2": push_message
            }
        )
        if 'errors' in rep.text:
            log.warning(f"推送执行错误：{rep.json()['errors']}")
            return 0
        else:
            log.info("推送完毕......")
        return 1

    def webhook(self, status_id, push_message):
        """
        WebHook
        """
        rep = self.http.post(
            url=f'{self.cfg.get("webhook", "webhook_url")}',
            headers={"Content-Type": "application/json; charset=utf-8"},
            json={
                "title": get_push_title(status_id),
                "message": push_message
            }
        ).json()
        log.info(f"推送结果：{rep.get('errmsg')}")

    def qmsg(self, status_id, push_message):
        """
        qmsg
        """
        rep = self.http.post(
            url=f'https://qmsg.zendee.cn/send/{self.cfg.get("qmsg", "key")}',
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data={
                "msg": get_push_title(status_id) + "\n" + push_message
            }
        ).json()
        log.info(f"推送结果：{rep['reason']}")

    def discord(self, status_id, push_message):
        import pytz

        def get_color() -> int:
            embed_color = 16744192
            if status_id == 0:  # 成功
                embed_color = 1926125
            elif status_id == 1:  # 全部失败
                embed_color = 14368575
            elif status_id == 2:  # 部分失败
                embed_color = 16744192
            elif status_id == 3:  # 触发验证码
                embed_color = 16744192
            return embed_color

        rep = self.http.post(
            url=f'{self.cfg.get("discord", "webhook")}',
            headers={"Content-Type": "application/json; charset=utf-8"},
            json={
                "content": None,
                "embeds": [
                    {
                        "title": get_push_title(status_id),
                        "description": push_message,
                        "color": get_color(),
                        "author": {
                            "name": "MihoyoBBSTools",
                            "url": "https://github.com/Womsxd/MihoyoBBSTools",
                            "icon_url": "https://github.com/DGP-Studio/Snap.Hutao.Docs/blob/main/docs/.vuepress/public"
                                        "/images/202308/hoyolab-miyoushe-Icon.png?raw=true "
                        },
                        "timestamp": datetime.now(timezone.utc).astimezone(pytz.timezone('Asia/Shanghai')).isoformat(),
                    }
                ],
                "username": "MihoyoBBSTools",
                "avatar_url": "https://github.com/DGP-Studio/Snap.Hutao.Docs/blob/main/docs/.vuepress/public/images"
                              "/202308/hoyolab-miyoushe-Icon.png?raw=true",
                "attachments": []
            }
        )
        if rep.status_code != 204:
            log.warning(f"推送执行错误：{rep.text}")
        else:
            log.info(f"推送结果：HTTP {rep.status_code} Success")

    def wintoast(self, status_id, push_message):
        try:
            from win11toast import toast
            toast(app_id="MihoyoBBSTools", title=get_push_title(status_id), body=push_message, icon='')
        except:
            log.error(f"请先pip install win11toast再使用win通知")

    def wxpusher(self, status_id, push_message):
        """
        WxPusher
        """
        try:
            from wxpusher import WxPusher
        except:
            log.error("WxPusher 模块未安装，请先执行pip install wxpusher")
            return 1
        app_token = self.cfg.get('wxpusher', 'app_token', fallback=None)
        uids = self.cfg.get('wxpusher', 'uids', fallback="").split(',')
        topic_ids = self.cfg.get('wxpusher', 'topic_ids', fallback="").split(',')
        if not app_token or not topic_ids:
            log.error("WxPusher 推送失败！请检查 app_token, topic_ids 是否正确配置")
            return 1
        response = WxPusher.send_message(
            content=get_push_title(status_id) + "\r\n" + push_message,
            uids=[uid for uid in uids if uid],  # 过滤空值
            topic_ids=[int(tid) for tid in topic_ids if tid.isdigit()],
            token=app_token
        )
        if "data" in response:
            status_list = [item.get("status", "未知状态") for item in response["data"]]
            log.info(f"WxPusher 推送状态：{status_list}")
            return 0
        else:
            log.error(f"WxPusher 推送失败：{response}")
            return 1

    def serverchan3(self, status_id, push_message):
        sendkey = self.cfg.get('serverchan3', 'sendkey')
        match = re.match(r'sctp(\d+)t', sendkey)
        if match:
            num = match.group(1)
            url = f'https://{num}.push.ft07.com/send/{sendkey}.send'
        else:
            raise ValueError('Invalid sendkey format for sctp')
        data = {
            'title': get_push_title(status_id),
            'desp': push_message,
            'tags': self.cfg.get('serverchan3', 'tags', fallback='')
        }
        rep = self.http.post(url=url, json=data)
        log.debug(rep.text)

    # 其他推送方法，例如 ftqq, pushplus 等, 和 telegram 方法相似
    # 在类内部直接使用 self.cfg 读取配置

    def push(self, status, push_message):
        if not self.load_config():
            return 1
        if not self.cfg.getboolean('setting', 'enable'):
            return 0
        if self.cfg.getboolean('setting', 'error_push_only', fallback=False) and status == 0:
            return 0
        log.info("正在执行推送......")
        func_names = self.cfg.get('setting', 'push_server').lower()
        push_success = True
        for func_name in func_names.split(","):
            func = getattr(self, func_name, None)
            if not func:
                log.warning(f"推送服务名称错误：{func_name}")
                continue
            log.debug(f"推送所用的服务为: {func_name}")
            try:
                if not config.update_config_need:
                    func(status, self.msg_replace(push_message))
                else:
                    func(-1,
                         f'如果您多次收到此消息开头的推送，证明您运行的环境无法自动更新config，请手动更新一下，谢谢\r\n'
                         f'{title.get(status, "")}\r\n{self.msg_replace(push_message)}')
            except Exception as e:
                log.warning(f"{func_name} 推送执行错误：{str(e)}")
                push_success = False
                continue
            log.info(f"{func_name} - 推送完毕......")
        return 0 if push_success else 1


def push(status, push_message):
    push_handler_instance = PushHandler()
    return push_handler_instance.push(status, push_message)


if __name__ == "__main__":
    push(0, f'推送验证{int(time.time())}')
