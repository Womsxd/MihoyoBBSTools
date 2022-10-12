"""
new Env('米游社');
"""
import notify
from loghelper import log
from error import CookieError
from main import main

if __name__ == "__main__":
    try:
        status_code, message = main()
    except CookieError:
        status_code = 1
        message = "账号Cookie出错！"
        log.error("账号Cookie有问题！")
    notify.send("米游社", message)

