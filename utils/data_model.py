'''
Author: Ljzd-PRO
Date: 2023-08-26 00:58:58
LastEditors: Night-stars-1 nujj1042633805@gmail.com
LastEditTime: 2023-08-31 16:16:48
Description: 
BY: @Ljzd-PRO https://github.com/Ljzd-PRO/nonebot-plugin-mystool
Copyright (c) 2023 by Night-stars-1, All Rights Reserved. 
'''
import inspect
from abc import abstractmethod
from typing import (TYPE_CHECKING, AbstractSet, Any, Dict, Literal, Mapping,
                    NamedTuple, Optional, Tuple, TypeVar, Union, no_type_check)

import orjson
from httpx import Cookies
from pydantic import BaseModel


class BaseModelWithSetter(BaseModel):
    """
    可以使用@property.setter的BaseModel

    目前pydantic 1.10.7 无法使用@property.setter
    issue: https://github.com/pydantic/pydantic/issues/1577#issuecomment-790506164
    """
    @no_type_check
    def __setattr__(self, name, value):
        try:
            super().__setattr__(name, value)
        except ValueError as e:
            setters = inspect.getmembers(
                self.__class__,
                predicate=lambda x: isinstance(x, property) and x.fset is not None
            )
            for setter_name, func in setters:
                if setter_name == name:
                    object.__setattr__(self, name, value)
                    break
            else:
                raise e

class BaseModelWithUpdate(BaseModel):
    """
    可以使用update方法的BaseModel
    """
    _T = TypeVar("_T", bound=BaseModel)

    @abstractmethod
    def update(self, obj: Union[_T, Dict[str, Any]]) -> _T:
        """
        更新数据对象

        :param obj: 新的数据对象或属性字典
        :raise TypeError
        """
        if isinstance(obj, type(self)):
            obj = obj.dict()
        items = filter(lambda x: x[0] in self.__fields__, obj.items())
        for k, v in items:
            setattr(self, k, v)
        return self
    
class GeetestResult(NamedTuple):
    """人机验证结果数据"""
    validate: str
    seccode: str

class AccountResult(BaseModel):
    """米游社账号信息"""
    game_biz: str
    """游戏biz"""
    region: str
    """游戏区服"""
    game_uid: str
    """游戏UID"""
    nickname: str
    """游戏昵称"""
    level: int
    """游戏等级"""
    region_name: str
    """游戏区服名称"""

class BaseApiStatus(BaseModel):
    """
    API返回结果基类
    """
    success = False
    """成功"""
    network_error = False
    """连接失败"""
    incorrect_return = False
    """服务器返回数据不正确"""
    login_expired = False
    """登录失效"""
    need_verify = False
    """需要进行人机验证"""
    invalid_ds = False
    """Headers DS无效"""

    def __bool__(self):
        if self.success:
            return True
        else:
            return False

class ApiResultHandler(BaseModel):
    """
    API返回的数据处理器
    """
    content: Dict[str, Any]
    """API返回的JSON对象序列化以后的Dict对象"""
    data: Optional[Dict[str, Any]]
    """API返回的数据体"""
    message: Optional[str]
    """API返回的消息内容"""
    retcode: Optional[int]
    """API返回的状态码"""

    def __init__(self, content: Dict[str, Any]):
        super().__init__(content=content)

        self.data = self.content.get("data")

        for key in ["retcode", "status"]:
            if not self.retcode:
                self.retcode = self.content.get(key)
                if self.retcode is None:
                    self.retcode = self.data.get(key) if self.data else None
                else:
                    break

        self.message: Optional[str] = None
        for key in ["message", "msg"]:
            if not self.message:
                self.message = self.content.get(key)
                if self.message is None:
                    self.message = self.data.get(key) if self.data else None
                else:
                    break

    @property
    def success(self):
        """
        是否成功
        """
        return self.retcode == 1 or self.message in ["成功", "OK"]

    @property
    def wrong_captcha(self):
        """
        是否返回验证码错误
        """
        return self.retcode in [-201, -302] or self.message in ["验证码错误", "Captcha not match Err"]

    @property
    def login_expired(self):
        """
        是否返回登录失效
        """
        return self.retcode in [-100, 10001] or self.message in ["登录失效，请重新登录"]

    @property
    def invalid_ds(self):
        """
        Headers里的DS是否无效
        """
        return self.message in ["invalid request"]

class CheckLoginHandler(BaseModel):
    """
    登录状态检测的数据处理器
    """
    content: Dict[str, Any]
    """API返回的JSON对象序列化以后的Dict对象"""
    data: Optional[Dict[str, Any]]
    """API返回的数据体"""
    message: Optional[str]
    """API返回的消息内容"""
    retcode: Optional[int]
    """API返回的状态码"""
    

    def __init__(self, content: Dict[str, Any]):
        super().__init__(content=content)

        self.data = self.content.get("data")

        if self.data is None:
            self.data = {
                "stat": "ExpiredCode"
            }

        for key in ["retcode", "status"]:
            if not self.retcode:
                self.retcode = self.content.get(key)
                if self.retcode is None:
                    self.retcode = self.data.get(key) if self.data else None
                else:
                    break

        self.message: Optional[str] = None
        for key in ["message", "msg"]:
            if not self.message:
                self.message = self.content.get(key)
                if self.message is None:
                    self.message = self.data.get(key) if self.data else None
                else:
                    break

    @property
    def success(self):
        """
        是否成功
        """
        return self.data.get("stat", "False") == "Confirmed"

    @property
    def game_token(self):
        """
        游戏TOKEN
        """
        if self.success:
            return orjson.loads(self.data['payload']['raw'])
        return None

    @property
    def scanned(self):
        """
        是否扫描
        """
        return self.data.get("stat", "False") in ["Scanned", "Confirmed"]

    @property
    def expiredCode(self):
        """
        是否过期
        """
        return self.data.get("stat", "False") == "ExpiredCode"

    def __bool__(self):
        if self.success:
            return True
        else:
            return False

class QrcodeLoginData(BaseModel):
    """
    二维码创建结果数据
    """
    app_id: str
    """登录的应用标识符"""
    ticket: str
    """结果数据里的TICKET"""
    device: str
    """设备ID"""
    url: str
    """二维码链接"""

if TYPE_CHECKING:
    IntStr = Union[int, str]
    DictIntStrAny = Dict[IntStr, Any]
    MappingIntStrAny = Mapping[IntStr, Any]
    AbstractSetIntStr = AbstractSet[IntStr]
    DictStrAny: Dict[str, Any]

class BBSCookies(BaseModel):
    """
    米游社Cookies数据
    """
    account_id: Optional[str]
    """米游社UID"""
    cookie_token: Optional[str]
    stoken: Optional[str]
    ltoken: Optional[str]
    mid: Optional[str]

    def __bool__(self):
        """判断Cookies是否存在"""
        if self.cookie_token and self.stoken and self.ltoken and self.mid:
            return True
        else:
            return False
        
    def dict(
        self,
        *,
        include: Optional[Union['AbstractSetIntStr', 'MappingIntStrAny']] = None,
        exclude: Optional[Union['AbstractSetIntStr', 'MappingIntStrAny']] = None,
        by_alias: bool = False,
        skip_defaults: Optional[bool] = None,
        exclude_unset: bool = False,
        exclude_defaults: bool = False,
        exclude_none: bool = False,
        cookie_type: bool = False
    ) -> 'DictStrAny':
        """
        获取Cookies字典
        """
        cookies_dict = super().dict(include=include, exclude=exclude, by_alias=by_alias, skip_defaults=skip_defaults,
                                    exclude_unset=exclude_unset, exclude_defaults=exclude_defaults,
                                    exclude_none=exclude_none)
        if cookie_type:
            # 去除空的字段
            empty_key = set()
            for key, value in cookies_dict.items():
                if not value:
                    empty_key.add(key)
            [cookies_dict.pop(key) for key in empty_key]
        return cookies_dict
