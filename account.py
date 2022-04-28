import config
import setting
from request import http
from loghelper import log
from error import CookieError


def game_id2name(game_id: str) -> str:
    try:
        return setting.game_id2name[game_id]
    except NameError:
        return game_id


def stop_module(game_id: str) -> None:
    if game_id == "bh2_cn":
        # config.honkai2rd_Auto_sign = False
        # 崩坏2功能敬请期待
        pass
    elif game_id == "bh3_cn":
        config.config["games"]["cn"]["honkai3rd"] = False
    elif game_id == "nxx_cn":
        # 未定好像没米游社签到
        pass
    elif game_id == "hk4e_cn":
        config.config["games"]["cn"]["genshin"] = False
    else:
        raise NameError
    config.save_config()


def get_account_list(game_id: str, headers: dict) -> list:
    log.info(f"正在获取米哈游账号绑定的{game_id2name(game_id)}账号列表...")
    temp_list = []
    req = http.get(setting.account_Info_url + game_id, headers=headers)
    data = req.json()
    if data["retcode"] != 0:
        log.warning(f"获取{game_id2name(game_id)}账号列表失败！")
        stop_module(game_id)
        raise CookieError("BBS Cookie Error")
    for i in data["data"]["list"]:
        temp_list.append([i["nickname"], i["game_uid"], i["region"]])
    log.info(f"已获取到{len(temp_list)}个{game_id2name(game_id)}账号信息")
    return temp_list
