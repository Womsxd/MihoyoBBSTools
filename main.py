import os
import time
import random
from typing import Tuple, Optional
from enum import Enum, auto

import push
import login
import tools
import config
import mihoyobbs
import cloudgames
import gamecheckin
import hoyo_checkin
import web_activity
import os_cloudgames
from loghelper import log
from error import CookieError, StokenError


class StatusCode(Enum):
    SUCCESS = 0
    FAILURE = 1
    PARTIAL_FAILURE = 2
    CAPTCHA_TRIGGERED = 3


def check_github_actions() -> None:
    """检查是否在GitHub Actions环境运行"""
    if os.getenv('GITHUB_ACTIONS') == 'true':
        log.error("请不要在 GitHub Action 运行本项目")
        exit(0)


def initialize_config() -> Tuple[bool, Optional[str]]:
    """初始化配置"""
    config.load_config()
    if not config.config["enable"]:
        log.warning("Config 未启用！")
        return False, "Config 未启用！"
    return True, None


def handle_login() -> None:
    """处理登录逻辑"""
    account_cfg = config.config["account"]
    if any([
        account_cfg["stuid"] == "",
        account_cfg["stoken"] == "",
        account_cfg["mid"] == ""
    ]):
        if config.config["mihoyobbs"]["enable"]:
            login.login()
            time.sleep(random.randint(3, 8))
        account_cfg["cookie"] = tools.tidy_cookie(account_cfg["cookie"])


def run_mihoyobbs() -> Tuple[str, bool]:
    """执行米游社签到任务"""
    return_data = ""
    raise_stoken = False

    if config.config["mihoyobbs"]["enable"]:
        if config.config["account"]["stoken"] == "StokenError":
            return_data = "米游社：\n账号 Stoken 异常"
            raise_stoken = True
        else:
            try:
                bbs = mihoyobbs.Mihoyobbs()
                return_data = bbs.run_task()
            except StokenError:
                raise_stoken = True
    return return_data, raise_stoken


def run_cn_tasks() -> str:
    """执行国服任务"""
    result = []
    if config.config["games"]['cn']["enable"]:
        result.append(gamecheckin.run_task())
    if config.config["cloud_games"]['cn']["enable"]:
        log.info("正在进行云游戏签到")
        result.append(cloudgames.run_task())
    return "\n\n".join(filter(None, result))


def run_os_tasks() -> str:
    """执行国际服任务"""
    result = []
    if config.config["games"]['os']["enable"]:
        log.info("海外版：")
        os_result = hoyo_checkin.run_task()
        if os_result:
            result.append(f"海外版：{os_result}")
    if config.config["cloud_games"]['os']["enable"]:
        log.info("正在进行云游戏国际版签到")
        result.append(os_cloudgames.run_task())
    return "\n\n".join(filter(None, result))


def run_web_activity() -> None:
    """执行网页活动任务"""
    if config.config["web_activity"]['enable']:
        log.info("正在进行米游社网页活动任务")
        web_activity.run_task()


def main() -> Tuple[int, str]:
    """主执行函数"""
    check_github_actions()

    success, msg = initialize_config()
    if not success:
        return StatusCode.FAILURE.value, msg

    handle_login()

    if config.config["account"]["cookie"] == "CookieError":
        raise CookieError('Cookie expires')

    return_data = []
    status_code = StatusCode.SUCCESS.value

    # 执行各模块任务
    mihoyo_result, raise_stoken = run_mihoyobbs()
    return_data.append(mihoyo_result)

    return_data.append(run_cn_tasks())
    return_data.append(run_os_tasks())

    run_web_activity()

    if raise_stoken:
        raise StokenError("Stoken 异常")

    result_msg = "\n".join(filter(None, return_data))
    if "触发验证码" in result_msg:
        status_code = StatusCode.CAPTCHA_TRIGGERED.value

    return status_code, result_msg


def task_run() -> None:
    """任务运行入口"""

    try:
        status_code, message = main()
        push_message = message
    except CookieError:
        status_code = StatusCode.FAILURE.value
        push_message = f"账号 Cookie 出错！\n{message}"
        log.error("账号 Cookie 有问题！")
    except StokenError:
        status_code = StatusCode.FAILURE.value
        push_message = f"账号 Stoken 出错！\n{message}"
        log.error("账号 Stoken 有问题！")

    push.push(status_code, push_message)


if __name__ == "__main__":
    task_run()
