import main
import push
import main_multi
from error import CookieError


def main_handler(event: dict, context: dict):
    try:
        status_code = main.main()
    except CookieError:
        status_code = 0
    push.push(status_code, "脚本已执行")
    print("云函数测试支持！")
    return 0


def main_handler_mulit(event: dict, context: dict):
    # 多用户需要传递True表示自动执行，不需要手动进行确认
    main_multi.main_multi(True)
    print("云函数多用户测试支持！")
    return 0
