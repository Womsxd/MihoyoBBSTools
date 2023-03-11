"""
new Env('米游社');
"""
import notify
import os
from loghelper import log
from error import CookieError
from main import main
from main_multi import main_multi

def single():
    title = "米游社"
    try:
        status_code, message = main()
        if status_code == 3:
            title = "米游社-触发验证码"
    except CookieError:
        title = "米游社-Cookie错误"
        message = "账号Cookie出错！"
        log.error("账号Cookie有问题！")
    notify.send(title, message)

def multi():
    status_code, message = main_multi(True)
    title = "米游社"
    if status_code == 1:
        title = "米游社-全部配置错误"
        log.error("全部配置文件错误！请检查配置文件！")
    elif status_code == 2:
        title = "米游社-部分配置错误"
        log.error("部分配置文件错误，请检查配置文件")
    elif status_code == 3:
        title = "米游社-触发验证码"
    notify.send(title, message)


if __name__ == "__main__":
    if os.getenv("AutoMihoyoBBS_config_multi") == "1":
        multi()
    else:
        single()
