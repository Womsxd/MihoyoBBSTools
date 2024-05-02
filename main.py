import os
import time
import random

import push
import login
import tools
import config
import mihoyobbs
import competition
import gamecheckin
import hoyo_checkin
import cloud_genshin
from error import *
from loghelper import log


def main():
    # 拒绝在GitHub Action运行
    if os.getenv('GITHUB_ACTIONS') == 'true':
        print("请不要在GitHub Action运行本项目")
        exit(0)
    # 初始化，加载配置
    return_data = "\n"
    config.load_config()
    if not config.config["enable"]:
        log.warning("Config未启用！")
        return 1, "Config未启用！"
    elif config.config["account"]["cookie"] == "CookieError":
        raise CookieError('Cookie expires')
    # 检测参数是否齐全，如果缺少就进行登入操作，同时判断是否开启开启米游社签到
    if (config.config["account"]["stuid"] == "" or config.config["account"]["stoken"] == "" or
            (login.require_mid() and config.config["account"]["mid"] == "")) and \
            config.config["mihoyobbs"]["enable"]:
        # 登入，如果没开启bbs全局没打开就无需进行登入操作
        if config.config["mihoyobbs"]["enable"]:
            login.login()
            time.sleep(random.randint(2, 8))
        # 整理 cookie，在字段重复时优先使用最后出现的值
        config.config["account"]["cookie"] = tools.tidy_cookie(config.config["account"]["cookie"])
    # 米游社签到
    ret_code = 0
    if config.config["mihoyobbs"]["enable"]:
        bbs = mihoyobbs.Mihoyobbs()
        return_data += bbs.run_task()
    # 国服
    if config.config['games']['cn']["enable"]:
        return_data += gamecheckin.run_task()
    # 国际
    if config.config['games']['os']["enable"]:
        log.info("海外版:")
        os_result = hoyo_checkin.run_task()
        if os_result != '':
            return_data += "\n\n" + "海外版:" + os_result
    # 云游戏
    if config.config['cloud_games']['genshin']["enable"] \
            and config.config['cloud_games']['genshin']['token'] != "":
        log.info("正在进行云原神签到")
        cloud_ys = cloud_genshin.CloudGenshin()
        data = cloud_ys.sign_account()
        return_data += "\n\n" + data
    if config.config['competition']['enable']:
        log.info("正在进行米游社竞赛活动签到")
        competition_result = competition.run_task()
        if competition_result != '':
            return_data += "\n\n" + "米游社竞赛活动:" + competition_result
    if "触发验证码" in return_data:
        ret_code = 3
    return ret_code, return_data


if __name__ == "__main__":
    try:
        status_code, message = main()
    except CookieError:
        status_code = 1
        message = "账号Cookie出错！"
        log.error("账号Cookie有问题！")
    push.push(status_code, message)
