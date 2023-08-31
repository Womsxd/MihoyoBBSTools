import asyncio
import random
from io import BytesIO
from string import ascii_letters, digits

import httpx
import uuid
import qrcode
from tenacity import Retrying, stop_after_attempt

from ..config import ConfigManager, write_plugin_data
from ..data_model import (ApiResultHandler, BBSCookies, CheckLoginHandler,
                          QrcodeLoginData)
from ..request import *
from ..utils import log
from .account_api import get_ltoken_by_stoken

_conf = ConfigManager.data_obj

QRCODE_FETCH_URL = "https://hk4e-sdk.mihoyo.com/hk4e_cn/combo/panda/qrcode/fetch"
QRCODE_QUERY_URL = "https://hk4e-sdk.mihoyo.com/hk4e_cn/combo/panda/qrcode/query"
GETCOOKIE_URL = "https://api-takumi.mihoyo.com/auth/api/getCookieAccountInfoByGameToken?game_token={game_token}&account_id={account_id}"

headers = {
    'x-rpc-app_version': _conf.salt.mihoyobbs_version,
    'x-rpc-aigis': '',
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    'x-rpc-game_biz': 'bbs_cn',
    'x-rpc-sys_version': "15.4",
    'x-rpc-device_id': uuid.uuid4().hex,
    #'x-rpc-device_fp':    ''.join(random.choices((ascii_letters + digits), k=13)),
    'x-rpc-device_name': "iPhone",
    'x-rpc-device_model': "iPhone10,2",
    'x-rpc-app_id': 'bll8iq97cem8',
    'x-rpc-client_type': '4',
    'User-Agent': "Hyperion/275 CFNetwork/1402.0.8 Darwin/22.2.0",
}

def generate_qrcode(url):
    qr = qrcode.QRCode(version=1,
                       error_correction=qrcode.constants.ERROR_CORRECT_L,
                       box_size=10,
                       border=4)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color='black', back_color='white')
    bio = BytesIO()
    img.save(bio)
    # 获取二维码的模块 (module) 列表
    qr_modules = qr.get_matrix()
    CHARS = ["  ", "██"]
    # 在控制台中打印二维码
    for row in qr_modules:
        line = "".join(CHARS[pixel] for pixel in row)
        log.success(line)

async def create_login_data():
    for attempt in Retrying(stop=stop_after_attempt(3)):
        with attempt:
            device_id = uuid.uuid4().hex
            app_id = '4'
            data = {
                'app_id': app_id,
                'device': device_id
            }
            res = await post(QRCODE_FETCH_URL,
                            json=data)
            api_result = ApiResultHandler(res.json())
            if api_result.retcode == 0:
                url: str = res.json()['data']['url']
                ticket = url.split('ticket=')[1]
                return QrcodeLoginData(app_id=app_id,ticket=ticket,device=device_id,url=url)
            else:
                raise Exception("二维码生成失败")


async def check_login(login_data: QrcodeLoginData, retry: bool = True):
    data = {
        'app_id': login_data.app_id,
        'ticket': login_data.ticket,
        'device': login_data.device
    }
    for attempt in Retrying(stop=stop_after_attempt(3)):
        with attempt:
            res = await post(QRCODE_QUERY_URL,
                    json=data)
            return CheckLoginHandler(res.json())

async def get_stoken(data: dict = None, retry: bool = True):
    if data is None:
        data = {}
    for attempt in Retrying(stop=stop_after_attempt(3)):
        with attempt:
            async with httpx.AsyncClient() as client:
                res = await client.post('https://passport-api.mihoyo.com/account/ma-cn-session/app/getTokenByGameToken',headers=headers,json=data)
            api_result = ApiResultHandler(res.json())
            if api_result.retcode == 0:
                return api_result.data
            else:
                raise Exception("获取stoken失败")
            
async def get_cookie_token(game_token: dict, retry: bool = True):
    for attempt in Retrying(stop=stop_after_attempt(3)):
        with attempt:
            res = await get(GETCOOKIE_URL.format(game_token=game_token['token'], 
                                                 account_id=game_token['uid']))
            api_result = ApiResultHandler(res.json())
            if api_result.retcode == 0:
                return api_result.data.get("cookie_token")
            else:
                raise Exception("获取cookie_token失败")

async def check_qrcode(login_data):
    while True:
        status_data = await check_login(login_data)
        log.info(status_data)
        if status_data:
            game_token = status_data.game_token
            cookie_token = await get_cookie_token(game_token)
            stoken_data = await get_stoken(data={'account_id': int(game_token['uid']),
                                                'game_token': game_token['token']})
            stoken = stoken_data['token']['token']
            mys_id = stoken_data['user_info']['aid']
            mid = stoken_data['user_info']['mid']
            _conf.mhy_data.cookie = BBSCookies.parse_obj({
                    "account_id": mys_id,
                    "cookie_token": cookie_token,
                    "stoken": stoken,
                    "mid": mid
                })
            write_plugin_data()
            login_status, cookies = await get_ltoken_by_stoken(_conf.mhy_data.cookie)
            if login_status:
                log.info(f"用户 {mys_id} 成功获取 ltoken: {cookies.ltoken}")
                _conf.mhy_data.cookie = cookies
                write_plugin_data()
            log.info(f"米游社账户 {mys_id} 添加成功")
            break
        await asyncio.sleep(5)

async def qr_login():
    if not _conf.mhy_data.cookie:
        login_data = await create_login_data()
        generate_qrcode(login_data.url)
        await check_qrcode(login_data)
