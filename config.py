import os
import json
import yaml
from loghelper import log

# 这个字段现在还没找好塞什么地方好，就先塞config这里了
serverless = False
# 提示需要更新config版本
update_config_need = False

config = {
    'enable': True, 'version': 7,
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
            'hokai2': {'auto_checkin': False, 'black_list': []},
            'honkai3rd': {'auto_checkin': False, 'black_list': []},
            'tears_of_themis': {'auto_checkin': False, 'black_list': []},
        },
        'os': {
            'enable': False, 'cookie': '',
            'genshin': {'auto_checkin': False, 'black_list': []}
        }
    },
    'cloud_games': {
        "genshin": {
            'enable': False,
            'token': ''
        }
    }
}

path = os.path.dirname(os.path.realpath(__file__)) + "/config"
if os.getenv("AutoMihoyoBBS_config_path") != "":
    path = os.getenv("AutoMihoyoBBS_config_path")
config_Path_json = f"{path}/config.json"
config_Path = f"{path}/config.yaml"
def copy_config():
    return config

def load_config_json():
    with open(config_Path_json, "r") as f:
        data = json.load(f)
        if data.get('version') == 5:
            config_json = data
            try:
                config_json["mihoyobbs"]["like_post"]
            except KeyError:
                pass
            else:
                config_json["mihoyobbs"]["read_posts"] = config_json["mihoyobbs"]["read_post"]
                config_json["mihoyobbs"]["like_posts"] = config_json["mihoyobbs"]["like_post"]
                del config_json["mihoyobbs"]["like_post"]
                del config_json["mihoyobbs"]["read_post"]
        else:
            log.error("config版本过低，请手动更新到基于yaml版本的新版本配置文件，更新完成后请删除json版的配置文件")
            exit(1)
        log.info("v5Config加载完毕")
        return config_json


def update_config():
    global config
    global update_config_need
    update_config_need = True
    log.info("正在更新config....")
    config_json = load_config_json()
    config['account'] = config_json['account']
    config['mihoyobbs'].update(config_json['mihoyobbs'])
    del config['mihoyobbs']['un_like']
    config['mihoyobbs']['cancel_like_posts'] = config_json['mihoyobbs']['un_like']
    for i in config_json['games']['cn'].keys():
        if i == 'enable':
            continue
        config['games']['cn'][i] = config_json['games']['cn'][i]
    config['games']['os'] = config_json['games']['os']
    config = config_v7_update(config)
    print(config)
    save_config()
    log.info('config更新完毕')
    if not serverless:
        os.remove(config_Path_json)
    else:
        log.error("请本地更新一下config")


def config_v7_update(data: dict):
    global update_config_need
    update_config_need = True
    data['version'] = 7
    data['cloud_games'] = {"genshin": {'enable': False, 'token': ''}}
    log.info("config已升级到: 7")
    return data


def load_config(p_path=None):
    global config
    if not p_path:
        p_path=config_Path
    with open(p_path, "r", encoding='utf-8') as f:
        data = yaml.load(f, Loader=yaml.FullLoader)
    if data['version'] == 7:
        config = data
    else:
        config = config_v7_update(data)
        save_config()
    log.info("Config加载完毕")
    return config


def save_config(p_path=None,p_config=None):
    global serverless
    if serverless:
        log.info("云函数执行，无法保存")
        return None
    if not p_path:
        p_path=config_Path
        p_config=config
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
    global serverless
    if serverless:
        log.info("云函数执行，无法保存")
        return None
    with open(config_Path, "r+") as f:
        config["enable"] = False
        config["account"]["login_ticket"] = ""
        config["account"]["stuid"] = ""
        config["account"]["stoken"] = ""
        config["account"]["cookie"] = "CookieError"
        try:
            f.seek(0)
            f.truncate()
            f.write(yaml.dump(config, Dumper=yaml.Dumper, sort_keys=False))
            f.flush()
        except OSError:
            serverless = True
            log.info("Cookie删除失败")
        else:
            log.info("Cookie删除完毕")


def clear_cookie_cloudgame():
    global config
    global serverless
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
    load_config()
    pass
