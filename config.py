import collections
import os
import yaml
import setting
from copy import deepcopy

import tools
from loghelper import log

# 这个字段现在还没找好塞什么地方好，就先塞config这里了
serverless = False
# 提示需要更新config版本
update_config_need = False

config = {
    'enable': True, 'version': 11,
    'account': {'cookie': '', 'stuid': '', 'stoken': '', 'mid': ''},
    'device': {'name': 'Xiaomi MI 6', 'model': 'Mi 6', 'id': ''},
    'mihoyobbs': {
        'enable': True, 'checkin': True, 'checkin_list': [5, 2],
        'read': True, 'like': True, 'cancel_like': True, 'share': True
    },
    'games': {
        'cn': {
            'enable': True,
            'useragent': 'Mozilla/5.0 (Linux; Android 12; Unspecified Device) AppleWebKit/537.36 (KHTML, like Gecko) '
                         'Version/4.0 Chrome/103.0.5060.129 Mobile Safari/537.36',
            'retries': 3,
            'genshin': {'checkin': True, 'black_list': []},
            'honkai2': {'checkin': False, 'black_list': []},
            'honkai3rd': {'checkin': False, 'black_list': []},
            'tears_of_themis': {'checkin': False, 'black_list': []},
            'honkai_sr': {'checkin': False, 'black_list': []},
            'zzz': {'checkin': False, 'black_list': []}
        },
        'os': {
            'enable': False, 'cookie': '', 'lang': 'zh-cn',
            'genshin': {'checkin': False, 'black_list': []},
            'honkai3rd': {'checkin': False, 'black_list': []},
            'tears_of_themis': {'checkin': False, 'black_list': []},
            'honkai_sr': {'checkin': False, 'black_list': []},
            'zzz': {'checkin': False, 'black_list': []}
        }
    },
    'cloud_games': {
        "genshin": {'enable': False, 'token': ''}
    },

    'competition': {
        'enable': False,
        'genius_invokation': {'enable': False, 'account': [], 'checkin': False, 'weekly': False}
    }
}
config_raw = deepcopy(config)

path = os.path.dirname(os.path.realpath(__file__)) + "/config"
if os.getenv("AutoMihoyoBBS_config_path") is not None:
    path = os.getenv("AutoMihoyoBBS_config_path")
config_prefix = os.getenv("AutoMihoyoBBS_config_prefix")
if config_prefix is None:
    config_prefix = ""
config_Path = f"{path}/{config_prefix}config.yaml"


def copy_config():
    return config_raw


def config_v8_update(data: dict):
    global update_config_need
    update_config_need = True
    returns = deepcopy(config)
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


def config_v9_update_to_v11(data: dict):
    global update_config_need
    update_config_need = True
    base_config = deepcopy(config_raw)

    base_config["enable"] = data["enable"]
    base_config['account'].update({key: value for key, value in data['account'].items()
                                   if key in base_config['account'].keys()})
    base_config['device']['id'] = tools.get_device_id(data['account']['cookie'])

    base_config['mihoyobbs'].update({
        'enable': data['mihoyobbs']['enable'],
        'checkin': data['mihoyobbs']['checkin'],
        'read': data['mihoyobbs']['read_posts'],
        'like': data['mihoyobbs']['like_posts'],
        'cancel_like': data['mihoyobbs']['cancel_like_posts'],
        'share': data['mihoyobbs']['share_post']
    })
    if data['mihoyobbs']['checkin_multi']:
        base_config['mihoyobbs']['checkin_list'] = data['mihoyobbs']['checkin_multi_list']
    else:
        base_config['mihoyobbs']['checkin_list'] = [5]

    for region, region_data in data['games'].items():
        region_config = base_config['games'][region]
        for item, item_data in region_data.items():
            if item not in ['enable', 'useragent', 'cookie', 'lang']:
                region_config[item] = {'checkin': item_data['auto_checkin'], 'black_list': item_data['black_list']}
            else:
                region_config[item] = item_data
    base_config['cloud_games'] = deepcopy(data['cloud_games'])
    log.info("config已升级到: 10")
    return base_config


def config_v10_update(data: dict):
    global update_config_need
    update_config_need = True
    data['version'] = 11
    data['account']['mid'] = ""
    genius = data['competition']['genius_invokation']
    new_keys = ['enable', 'account', 'checkin', 'weekly']
    data['competition']['genius_invokation'] = dict(collections.OrderedDict(
        (key, genius.get(key, False) if key != 'account' else []) for key in new_keys))
    log.info("config已升级到: 11")
    return data


def load_config(p_path=None):
    global config
    if not p_path:
        p_path = config_Path
    with open(p_path, "r", encoding='utf-8') as f:
        data = yaml.load(f, Loader=yaml.FullLoader)
    if data['version'] != config_raw['version']:
        if data['version'] == 7:
            data = config_v8_update(data)
        if data['version'] == 8:
            data = config_v9_update(data)
        if data['version'] == 9:
            data = config_v9_update_to_v11(data)
        if data['version'] == 10:
            data = config_v10_update(data)
        save_config(p_config=data)
    # 去除cookie最末尾的空格
    data["account"]["cookie"] = str(data["account"]["cookie"]).rstrip(' ')
    config = data
    log.info("Config加载完毕")
    return data


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
        else:
            log.info("Config保存完毕")


def clear_stoken():
    global config
    if serverless:
        log.info("云函数执行，无法保存")
        return None
    config["account"]["mid"] = ""
    config["account"]["stuid"] = ""
    config["account"]["stoken"] = "StokenError"
    log.info("Stoken已删除")
    save_config()


def clear_cookie():
    global config
    if serverless:
        log.info("云函数执行，无法保存")
        return None
    config["account"]["cookie"] = "CookieError"
    log.info(f"Cookie已删除")
    save_config()


def disable_games(region: str = "cn"):
    global config
    if serverless:
        log.info("云函数执行，无法保存")
        return None
    config['games'][region]['enable'] = False
    log.info(f"游戏签到({region})已关闭")
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
