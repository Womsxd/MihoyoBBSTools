import os
import json
from loghelper import log

# 这个字段现在还没找好塞什么地方好，就先塞config这里了
serverless = False

# 是否启用config
enable = True
# 这里的内容会自动获取
login_ticket = ""
stuid = ""
stoken = ""
# 这里是米游社的cookie
cookies = ""
# 这个dist里面的内容和米游社有关
mihoyobbs = {
    # 全局开关，关闭之后下面的都不执行
    "bbs_Global": True,
    # 讨论区签到
    "bbs_Signin": True,
    # 多个讨论区签到
    "bbs_Signin_multi": True,
    # 指定签到讨论区
    # 1是崩坏3 2是原神 3是崩坏2 4是未定事件簿 5是大别墅
    # 可以通过设置讨论区的id位置来设置主讨论区，[5,1]就是大别墅为主社区
    # 看帖子 点赞 分享帖子都是使用主社区获取到的列表
    "bbs_Signin_multi_list": [],
    # 浏览3个帖子
    "bbs_Read_posts": True,
    # 完成5次点赞
    "bbs_Like_posts": True,
    # 完成后取消点赞
    "bbs_Unlike": True,
    # 分享帖子
    "bbs_Share": True,
}
# 原神自动签到
genshin_Auto_sign = True
# 崩坏3自动签到
honkai3rd_Auto_sign = True

path = os.path.dirname(os.path.realpath(__file__)) + "/config"
config_Path = f"{path}/config.json"


def load_v4(data: dict):
    global enable
    global login_ticket
    global stuid
    global stoken
    global cookies
    global mihoyobbs
    global genshin_Auto_sign
    global honkai3rd_Auto_sign
    enable = data["enable_Config"]
    login_ticket = data["mihoyobbs_Login_ticket"]
    stuid = data["mihoyobbs_Stuid"]
    stoken = data["mihoyobbs_Stoken"]
    cookies = data["mihoyobbs_Cookies"]
    mihoyobbs = data["mihoyobbs"]
    genshin_Auto_sign = data["genshin_Auto_sign"]
    honkai3rd_Auto_sign = data["honkai3rd_Auto_sign"]


def load_config():
    with open(config_Path, "r") as f:
        data = json.load(f)
        if data.get('version') == 5:
            pass
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
        data["mihoyobbs_Login_ticket"] = login_ticket
        data["mihoyobbs_Stuid"] = stuid
        data["mihoyobbs_Stoken"] = stoken
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
