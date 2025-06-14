import os
import time
import random

import push
import login
import tools
import config
import mihoyobbs
import gamecheckin
import hoyo_checkin
import cloudgames
import os_cloudgames
import web_activity
from error import *
from loghelper import log


def main():
    # 拒绝在GitHub Action运行
    if os.getenv('GITHUB_ACTIONS') == 'true':
        print("请不要在 GitHub Action 运行本项目")
        exit(0)
    # 初始化，加载配置
    config.load_config()
    if not config.config["enable"]:
        log.warning("Config 未启用！")
        return 1, "Config 未启用！"
    # 检测参数是否齐全，如果缺少就进行登入操作
    if any([config.config["account"]["stuid"] == "", config.config["account"]["stoken"] == "",
            login.require_mid() and config.config["account"]["mid"] == ""]):
        # 登入，如果没开启bbs全局没打开就无需进行登入操作 (实际上也可以登录)
        if config.config["mihoyobbs"]["enable"]:
            login.login()
            time.sleep(random.randint(2, 8))
        # 整理 cookie，在字段重复时优先使用最后出现的值
        config.config["account"]["cookie"] = tools.tidy_cookie(config.config["account"]["cookie"])
    # 米游社签到
    ret_code = 0
    return_data = "\n"
    raise_stoken = False

    if config.config["mihoyobbs"]["enable"]:
        if config.config["account"]["stoken"] == "StokenError":
            raise_stoken = True
            return_data += "米游社：\n账号 Stoken 异常"
        else:
            try:
                bbs = mihoyobbs.Mihoyobbs()
                return_data += bbs.run_task()
            except StokenError:
                raise_stoken = True
    # 国服
    if config.config["account"]["cookie"] == "CookieError":
        raise CookieError('Cookie expires')
    if config.config['games']['cn']["enable"]:
        return_data += gamecheckin.run_task()
    # 云游戏
    if config.config['cloud_games']['cn']["enable"]:
        log.info("正在进行云游戏签到")
        return_data += "\n\n" + cloudgames.run_task()
    # 国际
    if config.config['games']['os']["enable"]:
        log.info("海外版：")
        os_result = hoyo_checkin.run_task()
        if os_result != '':
            return_data += "\n\n" + "海外版：" + os_result
    if config.config['cloud_games']['os']["enable"]:
        log.info("正在进行云游戏国际版签到")
        return_data += "\n\n" + os_cloudgames.run_task()
    if config.config['web_activity']['enable']:
        log.info("正在进行米游社网页活动任务")
        web_activity.run_task()
    if raise_stoken:
        raise StokenError("Stoken 异常")
    if "触发验证码" in return_data:
        ret_code = 3
    return ret_code, return_data


def task_run():
    push_message = ""
    message = ""
    try:
        status_code, message = main()
    except CookieError:
        status_code = 1
        push_message = "账号 Cookie 出错！\n"
        log.error("账号 Cookie 有问题！")
    except StokenError:
        status_code = 1
        push_message = "账号 Stoken 出错！\n"
        log.error("账号 Stoken 有问题！")
    push_message += message
    push.push(status_code, push_message)


if __name__ == "__main__":
    task_run()
