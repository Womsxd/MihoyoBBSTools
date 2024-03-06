import time
import random
import setting
import config
from request import get_new_session
from loghelper import log

RET_CODE_ALREADY_SIGNED_IN = -5003


def hoyo_checkin(event_base_url: str, act_id: str) -> str:
    """
    国际服游戏签到

    :param event_base_url: 基础Url
    :param act_id: 活动id
    :return: 签到结果
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

    info_list = http.get(info_url, headers=headers).json()

    today = info_list.get("data", {}).get("today")
    total_sign_in_day = info_list.get("data", {}).get("total_sign_day")
    already_signed_in = info_list.get("data", {}).get("is_sign")
    first_bind = info_list.get("data", {}).get("first_bind")

    if already_signed_in:
        log.info("今天已经签到过")
        ret_msg = "今天已经签到过"
        return ret_msg

    if first_bind:
        log.info("请手动签到一次")
        ret_msg = "请手动签到一次"
        return ret_msg

    awards_data = http.get(reward_url, headers=headers).json()

    awards = awards_data.get("data", {}).get("awards")

    log.info(f"准备签到: {today} ")

    # a normal human can't instantly click, so we wait a bit
    sleep_time = random.uniform(2.0, 10.0)
    log.debug(f"等待 {sleep_time}")
    time.sleep(sleep_time)

    response = http.post(sign_url, headers=headers, json={"act_id": act_id}).json()

    code = response.get("retcode", 99999)

    log.debug(f"return code {code}")

    if code == RET_CODE_ALREADY_SIGNED_IN:
        log.info("今天已经签到过")
        ret_msg = "今天已经签到过"
        return ret_msg
    elif code != 0:
        log.error(response['message'])
        ret_msg = response['message']
        return ret_msg

    reward = awards[total_sign_in_day - 1]

    log.info("签到成功")
    log.info(f"\t已连续签到{total_sign_in_day + 1}天")
    log.info(f"\t今天获得的奖励是: {reward['cnt']}x {reward['name']}")
    ret_msg = f"\t今天获得的奖励是: {reward['cnt']}x {reward['name']}"
    return ret_msg
    # logging.info(f"\tMessage: {response['message']}")


def genshin():
    log.info(f"正在进行原神签到")
    ret_msg = '原神:\n' + hoyo_checkin("https://sg-hk4e-api.hoyolab.com/event/sol",
                                     setting.os_genshin_act_id)
    return ret_msg


def honkai_sr():
    log.info(f"正在进行崩坏:星穹铁道签到")
    ret_msg = '崩坏:星穹铁道:\n' + hoyo_checkin("https://sg-public-api.hoyolab.com/event/luna/os",
                                          setting.os_honkai_sr_act_id)
    return ret_msg


def honkai3rd():
    log.info(f"正在进行崩坏3签到")
    ret_msg = '崩坏3:\n' + hoyo_checkin("https://sg-public-api.hoyolab.com/event/mani",
                                      setting.os_honkai3rd_act_id)
    return ret_msg


def tears_of_themis():
    log.info(f"正在进行未定事件簿签到")
    ret_msg = '未定事件簿:\n' + hoyo_checkin("https://sg-public-api.hoyolab.com/event/luna/os",
                                        setting.os_tearsofthemis_act_id)
    return ret_msg


def run_task():
    ret_msg = ''
    games = config.config['games']['os']

    if games['cookie'] == '':
        log.warning("国际服未配置Cookie!")
        games['enable'] = False
        config.save_config()
        return ''

    for game, data in games.items():
        if isinstance(data, dict) and data.get('checkin', False):
            try:
                ret_msg += f"\n\n{globals()[game]()}"
            except KeyError:
                pass

    return ret_msg
