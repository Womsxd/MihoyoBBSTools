import json
import random
import time
import logging

from hoyo_http import http_get_json, http_post_json


RET_CODE_ALREADY_SIGNED_IN = -5003


def hoyo_checkin(
    event_base_url: str,
    act_id: str,
    cookie_str: str
):

    lang = 'zh-cn'
    referer_url = "https://act.hoyolab.com/"
    reward_url = f"{event_base_url}/home?lang={lang}" \
                 f"&act_id={act_id}"
    info_url = f"{event_base_url}/info?lang={lang}" \
               f"&act_id={act_id}"
    sign_url = f"{event_base_url}/sign?lang={lang}"

    headers = {
        "Referer": referer_url,
        "Accept-Encoding": "gzip, deflate, br",
        "Cookie": cookie_str,
    }

    info_list = http_get_json(info_url, headers=headers)

    today = info_list.get("data", {}).get("today")
    total_sign_in_day = info_list.get("data", {}).get("total_sign_day")
    already_signed_in = info_list.get("data", {}).get("is_sign")
    first_bind = info_list.get("data", {}).get("first_bind")

    if already_signed_in:
        logging.info("今天已经签到过")
        ret_msg = "今天已经签到过"
        return ret_msg

    if first_bind:
        logging.info("请手动签到一次")
        ret_msg = "请手动签到一次"
        return ret_msg

    awards_data = http_get_json(reward_url)

    awards = awards_data.get("data", {}).get("awards")

    logging.info(f"准备签到: {today} ")

    # a normal human can't instantly click, so we wait a bit
    sleep_time = random.uniform(2.0, 10.0)
    logging.debug(f"等待 {sleep_time}")
    time.sleep(sleep_time)

    request_data = json.dumps({
        "act_id": act_id,
    }, ensure_ascii=False)

    response = http_post_json(sign_url, headers=headers, data=request_data)

    code = response.get("retcode", 99999)

    logging.debug(f"return code {code}")

    if code == RET_CODE_ALREADY_SIGNED_IN:
        logging.info("今天已经签到过")
        ret_msg = "今天已经签到过"
        return ret_msg
    elif code != 0:
        logging.error(response['message'])
        ret_msg = response['message']
        return ret_msg

    reward = awards[total_sign_in_day - 1]

    logging.info("签到成功")
    logging.info(f"\t已连续签到{total_sign_in_day + 1}天")
    logging.info(f"\t今天获得的奖励是: {reward['cnt']}x {reward['name']}")
    ret_msg = f"\t今天获得的奖励是: {reward['cnt']}x {reward['name']}"
    return ret_msg
    # logging.info(f"\tMessage: {response['message']}")