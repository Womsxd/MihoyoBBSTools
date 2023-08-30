import time
import random
import setting
from request import http
from loghelper import log

RET_CODE_ALREADY_SIGNED_IN = -5003


def hoyo_checkin(
        event_base_url: str,
        act_id: str,
        cookie_str: str
):
    reward_url = f"{event_base_url}/home?lang={setting.os_lang}" \
                 f"&act_id={act_id}"
    info_url = f"{event_base_url}/info?lang={setting.os_lang}" \
               f"&act_id={act_id}"
    sign_url = f"{event_base_url}/sign?lang={setting.os_lang}"

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
