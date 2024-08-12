import os
import sys
import main
import time
import push
import config
import random
import setting
from loghelper import log
from error import CookieError, StokenError


# 搜索配置文件
def find_config(ext: str) -> list:
    file_name = []
    for files in os.listdir(config.path):
        if os.path.splitext(files)[1] == ext:
            if config.config_prefix == "" or files.startswith(config.config_prefix):
                file_name.append(files)
    return file_name


# 筛选青龙多用户配置文件（头部匹配）
def ql_config(config_list: list):
    config_list_ql = []
    for files in config_list:
        if 'mhy_' == files[:4]:
            config_list_ql.append(files)
    return config_list_ql


def get_config_list() -> list:
    config_list = find_config('.yaml')
    if os.getenv("AutoMihoyoBBS_config_prefix") is None and os.getenv("AutoMihoyoBBS_config_multi") == '1':
        # 判断通过读取青龙目录环境变量来判断用户是否使用青龙面板
        if os.getenv("QL_DIR") is not None:
            config_list = ql_config(config_list)
    if len(config_list) == 0:
        log.warning("未检测到配置文件，请确认config文件夹存在.yaml后缀名的配置文件！")
        exit(1)
    return config_list


def main_multi(autorun: bool):
    log.info("AutoMihoyoBBS Multi User mode")
    log.info("正在搜索配置文件！")
    config_list = get_config_list()
    if autorun:
        log.info(f"已搜索到{len(config_list)}个配置文件，正在开始执行！")
    else:
        log.info(f"已搜索到{len(config_list)}个配置文件，请确认是否无多余文件！\r\n{config_list}")
        try:
            input("请输入回车继续，需要重新搜索配置文件请Ctrl+C退出脚本")
        except KeyboardInterrupt:
            exit(0)
    results = {"ok": [], "close": [], "error": [], "captcha": []}
    for i in iter(config_list):
        log.info(f"正在执行{i}")
        setting.mihoyobbs_List_Use = []
        config.config_Path = f"{config.path}/{i}"
        try:
            run_code, run_message = main.main()
        except (CookieError, StokenError):
            results["error"].append(i)
        else:
            if run_code == 0:
                results["ok"].append(i)
            elif run_code == 3:
                results["captcha"].append(i)
            else:
                results["close"].append(i)
        log.info(f"{i}执行完毕")
        time.sleep(random.randint(3, 10))
    print("")
    push_message = f'脚本执行完毕，共执行{len(config_list)}个配置文件，成功{len(results["ok"])}个，' \
                   f'没执行{len(results["close"])}个，失败{len(results["error"])}个' \
                   f'\r\n没执行的配置文件: {results["close"]}\r\n执行失败的配置文件: {results["error"]}\r\n' \
                   f'触发游戏签到验证码的配置文件: {results["captcha"]} '
    log.info(push_message)
    status = 0
    if len(results["error"]) == len(config_list):
        status = 1
    elif len(results["error"]) != 0:
        status = 2
    elif len(results["captcha"]) != 0:
        status = 3
    push.push(status, push_message)
    return status, push_message


if __name__ == "__main__":
    if (len(sys.argv) >= 2 and sys.argv[1] == "autorun") or os.getenv("AutoMihoyoBBS_autorun") == "1":
        autorun_flag = True
    else:
        autorun_flag = False
    main_multi(autorun_flag)
    exit(0)
