import login
import config
import setting
from error import CookieError
from request import http
from loghelper import log


def get_account_list(game_id: str, headers: dict, update: bool = False) -> list:
    game_name = setting.game_id2name.get(game_id, game_id)

    if update and login.update_cookie_token():
        headers['Cookie'] = config.config['account']['cookie']
    elif update:
        log.warning(f"获取{game_name}账号列表失败！")
        raise CookieError("BBS Cookie Error")

    log.info(f"正在获取米哈游账号绑定的{game_name}账号列表...")
    response = http.get(setting.account_Info_url, params={"game_biz": game_id}, headers=headers)
    data = response.json()
    if data["retcode"] == -100:
        return get_account_list(game_id, headers, update=True)

    if data["retcode"] != 0:
        log.warning(f"获取{game_name}账号列表失败！")
        return []

    account_list = []
    for i in data["data"]["list"]:
        account_list.append([i["nickname"], i["game_uid"], i["region"]])

    log.info(f"已获取到{len(account_list)}个{setting.game_id2name.get(game_id, game_id)}账号信息")
    return account_list
