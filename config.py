import os
import yaml
import setting
from loghelper import log

# 这个字段现在还没找好塞什么地方好，就先塞config这里了
serverless = False
# 提示需要更新config版本
update_config_need = False

config = {
    'enable': True, 'version': 9,
    'account': {
        'cookie': '',
        'login_ticket': '',
        'stuid': '',
        'stoken': ''
    },
    'mihoyobbs': {
        'enable': True, 'checkin': True, 'checkin_multi': True, 'checkin_multi_list': [2, 5],
        'read_posts': True, 'like_posts': True, 'cancel_like_posts': True, 'share_post': True
    },
    'games': {
        'cn': {
            'enable': True,
            'useragent': 'Mozilla/5.0 (Linux; Android 12; Unspecified Device) AppleWebKit/537.36 (KHTML, like Gecko) '
                         'Version/4.0 Chrome/103.0.5060.129 Mobile Safari/537.36',
            'genshin': {'auto_checkin': True, 'black_list': []},
            'honkai2': {'auto_checkin': False, 'black_list': []},
            'honkai3rd': {'auto_checkin': False, 'black_list': []},
            'tears_of_themis': {'auto_checkin': False, 'black_list': []},
            'honkai_sr': {'auto_checkin': False, 'black_list': []},
        },
        'os': {
            'enable': False, 'cookie': '',
            'genshin': {'auto_checkin': False, 'black_list': []},
            'honkai_sr': {'auto_checkin': False, 'black_list': []}
        }
    },
    'cloud_games': {
        "genshin": {
            'enable': False,
            'token': ''
        }
    }
}
config_raw = {}
config_raw.update(config)

path = os.path.dirname(os.path.realpath(__file__)) + "/config"
if os.getenv("AutoMihoyoBBS_config_path") is not None:
    path = os.getenv("AutoMihoyoBBS_config_path")
config_prefix = os.getenv("AutoMihoyoBBS_config_prefix")
if config_prefix is None:
    config_prefix = ""
config_Path = f"{path}/{config_prefix}config.yaml"


def copy_config():
    return config_raw


def config_v7_update(data: dict):
    global update_config_need
    update_config_need = True
    data['version'] = 7
    data['cloud_games'] = {"genshin": {'enable': False, 'token': ''}}
    log.info("config已升级到: 7")
    return data


def config_v8_update(data: dict):
    global update_config_need
    update_config_need = True
    returns = config.copy()
    returns["enable"] = data["enable"]
    returns["account"].update(data["account"])
    returns["mihoyobbs"].update(data["mihoyobbs"])
    returns["cloud_games"].update(data["cloud_games"])
    returns["games"]["os"].update(data["games"]["os"])
    for i in data['games']['cn'].keys():
        if i == "hokai2":
            returns['games']['cn']['honkai2'].update(data['games']['cn']['hokai2'])
            continue
        returns['games']['cn'][i] = data['games']['cn'][i]
    log.info("config已升级到: 8")
    return returns


def config_v9_update(data: dict):
    global update_config_need
    update_config_need = True
    data['version'] = 9
    data['games']['os'] = {
            'enable': False, 'cookie': '',
            'genshin': {'auto_checkin': False, 'black_list': []},
            'honkai_sr': {'auto_checkin': False, 'black_list': []}
        }
    log.info("config已升级到: 9")
    return data


def load_config(p_path=None):
    global config
    if not p_path:
        p_path = config_Path
    with open(p_path, "r", encoding='utf-8') as f:
        data = yaml.load(f, Loader=yaml.FullLoader)
    if data['version'] == 9:
        config = data
    else:
        if data['version'] == 6:
            data = config_v7_update(data)
        if data['version'] == 7:
            config = config_v8_update(data)
        if data['version'] == 8:
            config = config_v9_update(data)
        save_config()
    log.info("Config加载完毕")
    return config


def save_config(p_path=None, p_config=None):
    global serverless
    if serverless:
        log.info("云函数执行，无法保存")
        return None
    if not p_path:
        p_path = config_Path
    if not p_config:
        p_config = config
    with open(p_path, "w+") as f:
        try:
            f.seek(0)
            f.truncate()
            f.write(yaml.dump(p_config, Dumper=yaml.Dumper, sort_keys=False))
            f.flush()
        except OSError:
            serverless = True
            log.info("Cookie保存失败")
            exit(-1)
        else:
            log.info("Config保存完毕")


def clear_cookies():
    global config
    if serverless:
        log.info("云函数执行，无法保存")
        return None
    config["enable"] = False
    config["account"]["login_ticket"] = ""
    config["account"]["stuid"] = ""
    config["account"]["stoken"] = ""
    config["account"]["cookie"] = "CookieError"
    log.info("Cookie已删除")
    save_config()


def clear_cookie_game(game_id: str):
    global config
    if serverless:
        log.info("云函数执行，无法保存")
        return None
    config["account"]["cookie"] = "GameCookieError"
    config["games"]["cn"][setting.game_id2config[game_id]]["auto_checkin"] = False
    log.info(f"游戏签到Cookie已删除")
    save_config()


def clear_cookie_cloudgame():
    global config
    if serverless:
        log.info("云函数执行，无法保存")
        return None
    config['cloud_games']['genshin']["enable"] = False
    config['cloud_games']['genshin']['token'] = ""
    log.info("云原神Cookie删除完毕")
    save_config()


if __name__ == "__main__":
    # 初始化配置文件
    # try:
    #     account_cookie = config['account']['cookie']
    #     config = load_config()
    #     config['account']['cookie'] = account_cookie
    # except OSError:
    #     pass
    # save_config()
    # update_config()
    pass
