import main
import main_multi


def main_handler(event:dict, context:dict):
    main.main()
    print("云函数测试支持！")
    return 0

def main_handler_mulit(event:dict, context:dict):
    #多用户需要传递True表示自动执行，不需要手动进行确认
    main_multi.main_multi(True)
    print("云函数多用户测试支持！")
    return 0
