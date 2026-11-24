import time
import random
import logging
import setting
import config
from request import get_new_session
from loghelper import log

RET_CODE_ALREADY_SIGNED_IN = -5003


def hoyo_checkin(event_base_url: str, act_id: str) -> None:
    """
    国际服游戏签到

    :param event_base_url: 基础Url
    :param act_id: 活动id
    """
    os_lang = config.config["games"]["os"]["lang"]
    reward_url = f"{event_base_url}/home?lang={os_lang}" \
                 f"&act_id={act_id}"
    info_url = f"{event_base_url}/info?lang={os_lang}" \
               f"&act_id={act_id}"
    sign_url = f"{event_base_url}/sign?lang={os_lang}"

    http = get_new_session()

    cookie_str = config.config.get("games", {}).get("os", {}).get("cookie", "")

    headers = {
        "Referer": setting.os_referer_url,
        "Accept-Encoding": "gzip, deflate, br",
        "Cookie": cookie_str,
    }
    if act_id == setting.os_zzz_act_id:
        headers['x-rpc-signgame'] = "zzz"

    info_list = http.get(info_url, headers=headers).json()

    today = info_list.get("data", {}).get("today")
    total_sign_in_day = info_list.get("data", {}).get("total_sign_day")
    already_signed_in = info_list.get("data", {}).get("is_sign")
    first_bind = info_list.get("data", {}).get("first_bind")

    if already_signed_in:
        log.push("今天已经签到过")
        return

    if first_bind:
        log.push("请手动签到一次")
        return

    awards_data = http.get(reward_url, headers=headers).json()

    awards = awards_data.get("data", {}).get("awards")

    log.info(f"准备签到：{today} ")

    # a normal human can't instantly click, so we wait a bit
    sleep_time = random.uniform(2.0, 10.0)
    log.debug(f"等待 {sleep_time}")
    time.sleep(sleep_time)

    response = http.post(sign_url, headers=headers, json={"act_id": act_id}).json()

    code = response.get("retcode", 99999)

    log.debug(f"return code {code}")

    if code == RET_CODE_ALREADY_SIGNED_IN:
        log.push("今天已经签到过")
        return
    elif code != 0:
        log.push(response['message'], level=logging.ERROR)
        return

    reward = awards[total_sign_in_day - 1]

    log.push("签到成功")
    log.push(f"\t已连续签到 {total_sign_in_day + 1} 天")
    log.push(f"\t今天获得的奖励是：{reward['cnt']}x 「{reward['name']}」")


def genshin():
    log.info("正在进行「原神」签到")
    log.push('原神：')
    hoyo_checkin("https://sg-hk4e-api.hoyolab.com/event/sol", setting.os_genshin_act_id)


def honkai_sr():
    log.info("正在进行「崩坏：星穹铁道」签到")
    log.push('崩坏：星穹铁道：')
    hoyo_checkin("https://sg-public-api.hoyolab.com/event/luna/os", setting.os_honkai_sr_act_id)


def honkai3rd():
    log.info("正在进行「崩坏3」签到")
    log.push('崩坏3：')
    hoyo_checkin("https://sg-public-api.hoyolab.com/event/mani", setting.os_honkai3rd_act_id)


def tears_of_themis():
    log.info("正在进行「未定事件簿」签到")
    log.push('未定事件簿：')
    hoyo_checkin("https://sg-public-api.hoyolab.com/event/luna/os", setting.os_tearsofthemis_act_id)


def zzz():
    log.info("正在进行「绝区零」签到")
    log.push('绝区零：')
    hoyo_checkin("https://sg-act-nap-api.hoyolab.com/event/luna/zzz/os", setting.os_zzz_act_id)


def run_task() -> None:
    games = config.config['games']['os']

    if games['cookie'] == '':
        log.warning("国际服未配置 Cookie！")
        games['enable'] = False
        config.save_config()
        return

    game_funcs = [
        globals()[game] for game, data in games.items()
        if isinstance(data, dict) and data.get('checkin', False) and game in globals()
    ]
    if not game_funcs:
        return

    log.push("海外版：")
    for game_func in game_funcs:
        game_func()
