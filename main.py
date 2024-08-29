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
import wxmall
from error import *
from loghelper import log


def main():
    # 拒绝在GitHub Action运行
    if os.getenv('GITHUB_ACTIONS') == 'true':
        print("请不要在GitHub Action运行本项目")
        exit(0)
    # 初始化，加载配置
    config.load_config()
    if not config.config["enable"]:
        log.warning("Config未启用！")
        return 1, "Config未启用！"
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

    # 升级stoken
    if config.config["account"]["stoken"] != "" and not login.require_mid():
        try:
            login.update_stoken_v2()
        except StokenError:
            raise_stoken = True

    if config.config["mihoyobbs"]["enable"]:
        if config.config["account"]["stoken"] == "StokenError":
            raise_stoken = True
            return_data += "米游社: \n账号Stoken异常"
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
    # 微信商城签到
    if config.config['wxmall']['enable']:
        log.info("正在进行微信商城签到")
        wxmall_result = wxmall.run_task()
        if wxmall_result != '':
            return_data += "\n\n" + "微信商城签到:" + wxmall_result
    if raise_stoken:
        raise StokenError("Stoken异常")
    if "触发验证码" in return_data:
        ret_code = 3
    return ret_code, return_data


if __name__ == "__main__":
    push_message = ""
    message = ""
    try:
        status_code, message = main()
    except CookieError:
        status_code = 1
        push_message = "账号Cookie出错！\n"
        log.error("账号Cookie有问题！")
    except StokenError:
        status_code = 1
        push_message = "账号Stoken出错！\n"
        log.error("账号Stoken有问题！")
    push_message += message
    push.push(status_code, push_message)
