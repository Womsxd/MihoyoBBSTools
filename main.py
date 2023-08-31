'''
Author: Night-stars-1 nujj1042633805@gmail.com
Date: 2023-08-26 00:09:31
LastEditors: Night-stars-1 nujj1042633805@gmail.com
LastEditTime: 2023-08-31 16:11:17
Description: 

Copyright (c) 2023 by Night-stars-1, All Rights Reserved. 
'''
import asyncio

from utils.api.account_api import get_account_list
from utils.api.game_sign_api import BaseGameSign
from utils.api.login_api import qr_login
from utils.config import ConfigManager
from utils.utils import log

_conf = ConfigManager.data_obj

async def main():
    await qr_login()
    for basegame in BaseGameSign.AVAILABLE_GAME_SIGNS:
        account_list = await get_account_list(basegame.GAME_BIZ)
        for account in account_list:
            game_sign = basegame(account)
            await game_sign.sign()

if "__main__" == __name__:
    asyncio.run(main())
