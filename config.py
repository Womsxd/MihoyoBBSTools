import os
import json
from loghelper import log

# 这个字段现在还没找好塞什么地方好，就先塞config这里了
serverless = False

v5_config = '{"enable":false,"version":5,"account":{"cookie":"","login_ticket":"","stuid":"","stoken":""},"mihoyobbs":{' \
            '"enable":true,"checkin":true,"checkin_multi":true,"checkin_multi_list":[2,5],"read_posts":true,' \
            '"like_posts":true,"un_like":true,"share_post":true},"games":{"cn":{"enable":true,"hokai2":{' \
            '"auto_checkin":false,"black_list":[]},"honkai3rd":{"auto_checkin":false,"black_list":[]},' \
            '"tears_of_themis":{"auto_checkin":false,"black_list":[]},"genshin":{"auto_checkin":false,"black_list":[' \
            ']}},"os":{"enable":false,"cookie":"","genshin":{"auto_checkin":false,"black_list":[]}}}} '
config = json.loads(v5_config)

path = os.path.dirname(os.path.realpath(__file__)) + "/config"
config_Path = f"{path}/config.json"


def load_v4(data: dict):
    global config
    # 配置开关
    config["enable"] = data["enable_Config"]
    # 账号 cookie
    config["account"]["login_ticket"] = data["mihoyobbs_Login_ticket"]
    config["account"]["stuid"] = data["mihoyobbs_Stuid"]
    config["account"]["stoken"] = data["mihoyobbs_Stoken"]
    config["account"]["cookie"] = data["mihoyobbs_Cookies"]
    # bbs 相关设置(自己之前造的孽)
    config["mihoyobbs"]["enable"] = data["mihoyobbs"]["bbs_Global"]
    config["mihoyobbs"]["checkin"] = data["mihoyobbs"]["bbs_Signin"]
    config["mihoyobbs"]["checkin_multi"] = data["mihoyobbs"]["bbs_Signin_multi"]
    config["mihoyobbs"]["checkin_multi_list"] = data["mihoyobbs"]["bbs_Signin_multi_list"]
    config["mihoyobbs"]["read_post"] = data["mihoyobbs"]["bbs_Read_posts"]
    config["mihoyobbs"]["like_post"] = data["mihoyobbs"]["bbs_Like_posts"]
    config["mihoyobbs"]["un_like"] = data["mihoyobbs"]["bbs_Unlike"]
    config["mihoyobbs"]["share_post"] = data["mihoyobbs"]["bbs_Share"]
    # 游戏相关设置 v4只支持原神和崩坏3，所以其他选项默认关闭
    config["games"]["cn"]["genshin"] = data["genshin_Auto_sign"]
    config["games"]["cn"]["honkai3rd"] = data["honkai3rd_Auto_sign"]


def load_config():
    global config
    with open(config_Path, "r") as f:
        data = json.load(f)
        if data.get('version') == 5:
            config = data
        else:
            load_v4(data)
        f.close()
        log.info("Config加载完毕")


def save_config():
    global serverless
    if not serverless:
        log.info("云函数执行，无法保存")
        return None
    with open(config_Path, "r+") as f:
        data = json.load(f)
        data["mihoyobbs_Login_ticket"] = config["account"]["login_ticket"]
        data["mihoyobbs_Stuid"] = config["account"]["stuid"]
        data["mihoyobbs_Stoken"] = config["account"]["stoken"]
        temp_text = json.dumps(data, sort_keys=False, indent=4, separators=(', ', ': '))
        try:
            f.seek(0)
            f.truncate()
            f.write(temp_text)
            f.flush()
        except OSError:
            serverless = True
            log.info("Cookie保存失败")
            exit(-1)
        else:
            log.info("Config保存完毕")
        f.close()


def clear_cookies():
    global serverless
    if not serverless:
        log.info("云函数执行，无法保存")
        return None
    with open(config_Path, "r+") as f:
        data = json.load(f)
        data["enable_Config"] = False
        data["mihoyobbs_Login_ticket"] = ""
        data["mihoyobbs_Stuid"] = ""
        data["mihoyobbs_Stoken"] = ""
        data["mihoyobbs_Cookies"] = "CookieError"
        temp_text = json.dumps(data, sort_keys=False, indent=4, separators=(', ', ': '))
        try:
            f.seek(0)
            f.truncate()
            f.write(temp_text)
            f.flush()
        except OSError:
            serverless = True
            log.info("Cookie删除失败")
        else:
            log.info("Cookie删除完毕")
        f.close()
