import config
import setting
from request import http
from loghelper import log
from error import CookieError


def get_account_list(game_id: str, headers: dict) -> list:
    log.info(f"正在获取米哈游账号绑定的{setting.game_id2name.get(game_id, game_id)}账号列表...")
    temp_list = []
    req = http.get(setting.account_Info_url, params={"game_biz": game_id}, headers=headers)
    data = req.json()
    if data["retcode"] != 0:
        log.warning(f"获取{setting.game_id2name.get(game_id, game_id)}账号列表失败！")
        config.clear_cookie_game(game_id)
        raise CookieError("BBS Cookie Error")
    for i in data["data"]["list"]:
        temp_list.append([i["nickname"], i["game_uid"], i["region"]])
    log.info(f"已获取到{len(temp_list)}个{setting.game_id2name.get(game_id, game_id)}账号信息")
    return temp_list
