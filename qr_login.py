import json
import time
import config
import setting
from request import http
import tools
import random
from string import ascii_letters, digits
from qrcode.main import QRCode
from typing import Tuple, TypedDict, Literal
from io import StringIO
from loghelper import log
import uuid

HEADERS_QRCODE_API = {
    "x-rpc-app_version": setting.mihoyobbs_version,
    "DS": None,
    "x-rpc-aigis": "",
    "Content-Type": "application/json",
    "Accept": "application/json",
    "x-rpc-game_biz": "bbs_cn",
    "x-rpc-sys_version": "12",
    "x-rpc-device_id": uuid.uuid4().hex,
    "x-rpc-device_name": config.config["device"]["name"],
    "x-rpc-device_model": config.config["device"]["model"],
    "x-rpc-app_id": "bll8iq97cem8",
    "x-rpc-client_type": "4",
    "User-Agent": "okhttp/4.9.3",
}

TOKEN_BY_GAME_TOKEN_URL = (
    "https://api-takumi.mihoyo.com/account/ma-cn-session/app/getTokenByGameToken"
)
CHECK_QR_URL = "https://hk4e-sdk.mihoyo.com/hk4e_cn/combo/panda/qrcode/query"
QR_URL = "https://hk4e-sdk.mihoyo.com/hk4e_cn/combo/panda/qrcode/fetch"


class PayloadRaw(TypedDict):
    uid: str
    """用户ID"""
    token: str
    """游戏Token"""


class PayLoad(TypedDict):
    proto: Literal["Account", "Raw"]
    raw: PayloadRaw
    ext: str


class CheckQRResult(TypedDict):
    stat: str
    """状态"""
    payload: PayLoad
    realname_info: dict


class StokenDataTokenResult(TypedDict):
    token_type: int
    """SToken类型"""
    token: str
    """SToken"""


class StokenDataUserInfoResult(TypedDict):
    aid: str
    """用户ID"""
    mid: str
    """用户代号"""


class StokenDataResult(TypedDict):
    token: StokenDataTokenResult
    user_info: StokenDataUserInfoResult
    realname_info: dict
    need_realperson: bool


class StokenResult(TypedDict):
    retcode: int
    message: str
    data: StokenDataResult


def get_qr_url() -> Tuple[str, str, str]:
    """
    说明:
        获取二维码URL
    """
    app_id = "4"
    device = "".join(random.choices((ascii_letters + digits), k=64))
    _json = {
        "app_id": app_id,
        "device": device,
    }
    response = http.post(QR_URL, json=_json)
    result = response.json()
    data = result["data"]
    qr_url: str = data["url"]
    ticket = qr_url.split("ticket=")[1]
    return qr_url, app_id, ticket, device


def check_login(app_id: str, ticket: str, device: str):
    """
    说明:
        检查二维码登录状态
    参数:
        :param app_id: 来自`get_qr_url`的`_json`
        :param ticket: 来自`get_qr_url`
        :param device: 设备ID
    """
    # {'stat': 'Init', 'payload': {'proto': 'Raw', 'raw': '', 'ext': ''}, 'realname_info': None}
    # {'stat': 'Scanned', 'payload': {'proto': 'Raw', 'raw': '', 'ext': ''}, 'realname_info': None}
    # {'stat': 'Confirmed', 'payload': {'proto': 'Account', 'raw': '{"uid":"","token":""}', 'ext': ''}, 'realname_info': None}
    while True:
        _json = {"app_id": app_id, "ticket": ticket, "device": device}
        response = http.post(CHECK_QR_URL, json=_json)
        result = response.json()
        data: CheckQRResult = result["data"]
        # match python>=3.10
        match data["stat"]:
            case "Init":
                log.info("等待扫码")
            case "Scanned":
                log.info("等待确认")
            case "Confirmed":
                log.info("登录成功")
                raw = json.loads(data["payload"]["raw"])
                game_token = raw["token"]
                uid = raw["uid"]
                return uid, game_token
            case _:
                log.error("未知的状态")
                raise ValueError("未知的状态")
        time.sleep(1)


def show_qrcode(qr_url: str):
    """
    说明:
        显示二维码
    参数:
        :param qr_url: 二维码URL
    """
    qr = QRCode()
    qr.add_data(qr_url)
    f = StringIO()
    qr.print_ascii(out=f)
    f.seek(0)
    print(f.read())


def get_stoken_by_game_token(uid: str, game_token: str):
    """
    说明:
        获取stoken
    参数:
        :param uid: 用户ID
        :param game_token: 游戏Token
    """
    headers = HEADERS_QRCODE_API.copy()
    _json = {"account_id": int(uid), "game_token": game_token}
    headers["DS"] = tools.get_ds2(body=json.dumps(_json))
    response = http.post(
        TOKEN_BY_GAME_TOKEN_URL,
        headers=headers,
        json=_json,
    )
    result: StokenResult = response.json()
    data = result["data"]
    return data["token"]["token"]


if __name__ == "__main__":
    qr_url, app_id, ticket, device = get_qr_url()
    show_qrcode(qr_url)
    uid, game_token = check_login(app_id, ticket, device)
    stoken = get_stoken_by_game_token(uid, game_token)
    print(f"{uid=}, {game_token=}, {stoken=}")
