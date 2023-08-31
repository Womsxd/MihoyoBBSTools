'''
Author: Night-stars-1 nujj1042633805@gmail.com
Date: 2023-08-26 00:17:30
LastEditors: Night-stars-1 nujj1042633805@gmail.com
LastEditTime: 2023-08-31 14:52:13
Description: 

Copyright (c) 2023 by Night-stars-1, All Rights Reserved. 
'''
import os
from pathlib import Path

from typing import Optional, Union, TYPE_CHECKING, Dict, Any, Mapping, AbstractSet
from orjson import JSONDecodeError
from pydantic import BaseModel, BaseSettings, ValidationError, validator

from loguru import logger as log

from .data_model import BBSCookies

ROOT_PATH = Path(__name__).parent.absolute()

DATA_PATH = ROOT_PATH / "data"
'''数据保存目录'''

CONFIG_PATH = DATA_PATH / "config.json"
"""数据文件默认路径"""


class Preference(BaseSettings):
    abc: int = 1
    timeout: int = 10
    """超时时间"""
    geetest_url: str = ""
    """打码平台地址"""
    
class MHY_DATA(BaseModel):
    cookie: BBSCookies = BBSCookies()
    """米游社cookie"""

class SALT(BaseModel):
    mihoyobbs_salt = "xc1lzZFOBGU0lz8ZkPgcrWZArZzEVMbA"
    mihoyobbs_salt_x4 = "xV8v4Qu54lUKrEYFZkJhB8cuOh9Asafs"
    mihoyobbs_salt_x6 = "t0qEgfub6cvueAPgR5m9aQWWVciEer7v"

    mihoyobbs_salt_web = "F6tsiCZEIcL9Mor64OXVJEKRRQ6BpOZa"
    """网页端Salt"""
    mihoyobbs_version: str = "2.55.1"
    """米游社版本号"""

class Config(BaseModel):
    preference: Preference = Preference()
    """偏好设置"""
    mhy_data: MHY_DATA = MHY_DATA()
    """米哈游数据"""
    salt: SALT = SALT()
    """Salt和Version相互对应"""

def write_plugin_data(data: Config = None):
    """
    写入插件数据文件

    :param data: 配置对象
    """
    if data is None:
        data = ConfigManager.data_obj
    try:
        str_data = data.json(indent=4)
    except (AttributeError, TypeError, ValueError):
        log.exception("数据对象序列化失败，可能是数据类型错误")
        return False
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        f.write(str_data)
    return True

class ConfigManager:
    data_obj = Config()
    """加载出的插件数据对象"""

    @classmethod
    def load_config(cls):
        """
        加载插件数据文件
        """
        if os.path.exists(DATA_PATH) and os.path.isfile(CONFIG_PATH):
            try:
                new_model = Config.parse_file(CONFIG_PATH)
                for attr in new_model.__fields__:
                    ConfigManager.data_obj.__setattr__(attr, new_model.__getattribute__(attr))
                write_plugin_data(ConfigManager.data_obj) # 同步配置
            except (ValidationError, JSONDecodeError):
                log.exception(f"读取数据文件失败，请检查数据文件 {CONFIG_PATH} 格式是否正确")
                raise
            except:
                log.exception(
                    f"读取数据文件失败，请检查数据文件 {CONFIG_PATH} 是否存在且有权限读取和写入")
                raise
        else:
            config_data = Config()
            try:
                str_data = config_data.json(indent=4)
                if not os.path.exists(DATA_PATH):
                    os.mkdir(DATA_PATH)
                with open(CONFIG_PATH, "w", encoding="utf-8") as f:
                    f.write(str_data)
            except (AttributeError, TypeError, ValueError, PermissionError):
                log.exception(f"创建数据文件失败，请检查是否有权限读取和写入 {CONFIG_PATH}")
                raise
            log.info(f"数据文件 {CONFIG_PATH} 不存在，已创建默认数据文件。")

ConfigManager.load_config()
