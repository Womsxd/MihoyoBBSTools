import os
import time
import push
import login
import config
import random
import honkai2
import genshin
import setting
import honkaisr
import hoyo_sr
import hoyo_gs
import mihoyobbs
import honkai3rd
import tearsofthemis
import cloud_genshin
from error import *
from loghelper import log


def checkin_game(game_name, game_module, game_print_name=""):
    if config.config["games"]["cn"][game_name]["auto_checkin"]:
        time.sleep(random.randint(2, 8))
        if game_print_name == "":
            game_print_name = game_name
        log.info(f"正在进行{game_print_name}签到")
        return_data = f"\n\n{game_module().sign_account()}"
        return return_data
    return ""


def run_bbs():
    return_data = "米游社: "
    bbs = mihoyobbs.Mihoyobbs()
    if bbs.task_do["bbs_sign"] and bbs.task_do["bbs_read"] and bbs.task_do["bbs_like"] and \
            bbs.task_do["bbs_share"]:
        return_data += "\n" + f"今天已经全部完成了！\n" \
                              f"一共获得{bbs.today_have_get_coins}个米游币\n目前有{bbs.have_coins}个米游币"
        log.info(f"今天已经全部完成了！一共获得{bbs.today_have_get_coins}个米游币，目前有{bbs.have_coins}个米游币")
    else:
        i = 0
        while bbs.today_get_coins != 0 and i < 3:
            if i > 0:
                bbs.refresh_list()
            if config.config["mihoyobbs"]["checkin"]:
                bbs.signing()
            if config.config["mihoyobbs"]["read_posts"]:
                bbs.read_posts()
            if config.config["mihoyobbs"]["like_posts"]:
                bbs.like_posts()
            if config.config["mihoyobbs"]["share_post"]:
                bbs.share_post()
            bbs.get_tasks_list()
            i += 1
        return_data += "\n" + f"今天已经获得{bbs.today_have_get_coins}个米游币\n" \
                              f"还能获得{bbs.today_get_coins}个米游币\n目前有{bbs.have_coins}个米游币"
        log.info(f"今天已经获得{bbs.today_have_get_coins}个米游币，"
                 f"还能获得{bbs.today_get_coins}个米游币，目前有{bbs.have_coins}个米游币")
        time.sleep(random.randint(2, 8))
    return return_data


def main():
    # 拒绝在GitHub Action运行
    if os.getenv('GITHUB_ACTIONS') == 'true':
        print("请不要在GitHub Action运行本项目")
        exit(0)
    # 初始化，加载配置
    return_data = "\n"
    config.load_config()
    if config.config["enable"]:
        # 检测参数是否齐全，如果缺少就进行登入操作
        if config.config["account"]["login_ticket"] == "" or config.config["account"]["stuid"] == "" or \
                config.config["account"]["stoken"] == "":
            # 整理 cookie，在字段重复时优先使用最后出现的值
            cookie_dict = {}
            for cookie in config.config["account"]["cookie"].split(";"):
                cookie = cookie.strip()
                if cookie == "":
                    continue
                key, value = cookie.split("=", 1)
                cookie_dict[key] = value
            config.config["account"]["cookie"] = "; ".join([f"{key}={value}" for key, value in cookie_dict.items()])
            # 登入，如果没开启bbs全局没打开就无需进行登入操作
            if config.config["mihoyobbs"]["enable"]:
                login.login()
            time.sleep(random.randint(2, 8))
        # 获取要使用的BBS列表,#判断是否开启bbs_Signin_multi
        if config.config["mihoyobbs"]["checkin_multi"]:
            # 用这里的方案可以实现当让id在第一个的时候为主社区
            for i in config.config["mihoyobbs"]["checkin_multi_list"]:
                for i2 in setting.mihoyobbs_List:
                    if i == int(i2["id"]):
                        setting.mihoyobbs_List_Use.append(i2)
        else:
            # 关闭bbs_Signin_multi后只签到大别墅
            for i in setting.mihoyobbs_List:
                if int(i["id"]) == 5:
                    setting.mihoyobbs_List_Use.append(i)
        # 米游社签到
        ret_code = 0
        if config.config["mihoyobbs"]["enable"]:
            return_data += run_bbs()
        # 国服
        if config.config['games']['cn']["enable"]:
            # 崩坏2签到
            return_data += checkin_game("honkai2", honkai2.Honkai2, "崩坏学园2")
            # 崩坏3签到
            return_data += checkin_game("honkai3rd", honkai3rd.Honkai3rd, "崩坏3rd")
            # 未定事件簿签到
            return_data += checkin_game("tears_of_themis", tearsofthemis.Tears_of_themis, "未定事件簿")
            # 原神签到
            return_data += checkin_game("genshin", genshin.Genshin, "原神")
            # 崩铁
            return_data += checkin_game("honkai_sr", honkaisr.Honkaisr, "崩坏: 星穹铁道")
        # 国际
        if config.config['games']['os']["enable"]:
            log.info("海外版:")
            return_data += "\n\n" + "海外版:"
            if config.config['games']['os']['genshin']["auto_checkin"]:
                log.info("正在进行原神签到")
                data = hoyo_gs.run()
                return_data += "\n\n" + data
            if config.config['games']['os']['honkai_sr']["auto_checkin"]:
                log.info("正在进行崩坏:星穹铁道签到")
                data = hoyo_sr.run()
                return_data += "\n\n" + data
        # 云游戏
        if config.config['cloud_games']['genshin']["enable"] \
                and config.config['cloud_games']['genshin']['token'] != "":
            log.info("正在进行云原神签到")
            cloud_ys = cloud_genshin.CloudGenshin()
            data = cloud_ys.sign_account()
            return_data += "\n\n" + data
        if "触发验证码" in return_data:
            ret_code = 3
        return ret_code, return_data
    elif config.config["account"]["cookie"] == "CookieError":
        raise CookieError('Cookie expires')
    else:
        log.warning("Config未启用！")
        return 1, "Config未启用！"


if __name__ == "__main__":
    try:
        status_code, message = main()
    except CookieError:
        status_code = 1
        message = "账号Cookie出错！"
        log.error("账号Cookie有问题！")
    push.push(status_code, message)
