import main
import push
import config
import main_multi
from error import CookieError


def main_handler(event: dict, context: dict):
    config.serverless = True
    try:
        status_code, push_message = main.main()
    except CookieError:
        status_code = 0
    push.push(status_code, push_message)
    print("云函数测试支持！")
    return 0


def main_handler_mulit(event: dict, context: dict):
    config.serverless = True
    # 多用户需要传递True表示自动执行，不需要手动进行确认
    main_multi.main_multi(True)
    print("云函数多用户测试支持！")
    return 0
