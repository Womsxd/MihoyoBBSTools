'''
Author: Night-stars-1 nujj1042633805@gmail.com
Date: 2023-08-31 19:05:23
LastEditors: Night-stars-1 nujj1042633805@gmail.com
LastEditTime: 2023-09-21 20:29:18
Description: 

Copyright (c) 2023 by Night-stars-1, All Rights Reserved. 
'''
import re
from urllib.parse import unquote, urlparse

import httpx
from loghelper import logger

AJGEETEST_URL = "https://security.weibo.com/captcha/ajgeetest"
SIGN_URL = "https://api.weibo.cn/2/page/button"
DRAW_URL = 'https://games.weibo.cn/prize/aj/lottery'
EVENT_URL = 'https://m.weibo.cn/api/container/getIndex?containerid={container_id}_-_activity_list'
HEADERS = {
    "user-agent": "Mozilla/5.0 (Linux; Android 13; 21121210C Build/TKQ1.220807.001; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/116.0.0.0 Mobile Safari/537.36 Weibo (Xiaomi-21121210C__weibo__11.6.3__android__android13)"
}


def nested_lookup(obj, key, with_keys=False, fetch_first=False):
    result = list(_nested_lookup(obj, key, with_keys=with_keys))
    if with_keys:
        values = [v for k, v in _nested_lookup(obj, key, with_keys=with_keys)]
        result = {key: values}
    if fetch_first:
        result = result[0] if result else result
    return result

def _nested_lookup(obj, key, with_keys=False):
    if isinstance(obj, list):
        for i in obj:
            yield from _nested_lookup(i, key, with_keys=with_keys)

    if isinstance(obj, dict):
        for k, v in obj.items():
            if key == k:
                if with_keys:
                    yield k, v
                else:
                    yield v

            if isinstance(v, list) or isinstance(v, dict):
                yield from _nested_lookup(v, key, with_keys=with_keys)

class WeiBo:
    def __init__(self) -> None:
        self.name = "未知"
        self.container_id = ""
        # Cookie
        self.aid = '.'
        self.wfrom = ''
        self.gsid = ''
        self.s = ''
        self.cookies = {
            "SUB": "",
            "SUBP": ""
        }

    @property
    def event_list(self):
        url = EVENT_URL.format(container_id=self.container_id)
        response = httpx.get(url)
        result: dict = response.json()
        cards = nested_lookup(result, 'group', fetch_first=True)
        return cards if '一键参与' and '年度超话' not in str(cards) else False


    def follow_data(self):
        url = 'https://api.weibo.cn/2/cardlist'
        params = {
            'c': 'android',
            'request_url': 'http://i.huati.weibo.com/mobile/super/active_checkin?pageid=100808e1f868bf9980f09ab6908787d7eaf0f0',
            's': self.s,
            'gsid': self.gsid,
            'from': self.wfrom,
        }
        params['containerid'] = '100803_-_followsuper'
        header = HEADERS.copy()
        response = httpx.get(url, params=params, headers=header)
        result = response.json()
        cards = result.get("cards", [])
        if len(cards) > 0:
            card_group = cards[0].get("card_group", [])
            follows = [{
                'name': card["title_sub"],
                'level': card["desc1"],
                'is_sign': False if card["buttons"][0]["name"] == '签到' else True,
                'containerid': ''.join(re.findall('containerid=(.*)&', card["scheme"]))
            }for card in card_group if card.get("card_type") == "8"]
        return follows or []

    def sign(self, pageid):
        params = {
            'c': 'android',
            'request_url': f'http://i.huati.weibo.com/mobile/super/active_checkin?pageid={pageid}&in_page=1',
            's': self.s, # '4e8f5db0', # '836ef048'
            'gsid': self.gsid, # '_2A25O7hkIDeRxGeFN7FQX9SvIzTuIHXVruivArDV6PUJbkdAGLWv9kWpNQ8OYu4Y7Jr5DXzKZoHYgJVnU4zL_Np_K', # '_2A25J-NKiDeRxGeFG61cZ8yrJzDmIHXVorGFqrDV6PUJbkdAGLXHxkWpNfntNT3Jq0wVB5dFKnESnKqLmwbHcmFrb',
            'from': self.wfrom,
        }
        header = HEADERS.copy()
        res = httpx.get(
            SIGN_URL,
            params=params,
            headers=header
        )
        api_result: dict = res.json()
        logger.debug(api_result)
        if api_result.get("result") == 402004:
            logger.info(f"{self.name} - 出现验证码")
            scheme = urlparse(api_result.get('scheme'))
            key = scheme.query.replace("key=", "")
            result = httpx.post(
                "",
                json={
                    "key": key
                },
                timeout=60
            )
            logger.debug(result.text)
            self.sign(pageid=pageid)
        elif api_result.get("result") == '1':
            logger.success(f"{self.name} - 签到成功")
        elif api_result.get("errno"):
            logger.info(f"{self.name} - {api_result.get('errmsg')}")
        else:
            logger.error(f"{self.name} - 签到失败")

    def get_event_gift_ids(self):
        self.event_list
        return [
            i
            for event in self.event_list
            for i in re.findall(r'ticket_id=(\d*)', unquote(unquote(event['scheme'])))
        ]

    def unclaimed_gift_ids(self):
        event_gift_ids = self.get_event_gift_ids()
        return event_gift_ids

    def get_code(self, id: str):
        header = HEADERS.copy()
        params = {
            'ext': '',
            'ticket_id': id,
            'aid': self.aid,
            'from': self.wfrom
        }
        response = httpx.get(
            DRAW_URL,
            params=params,
            headers=header,
            cookies=self.cookies
        )
        if 'html' in response.text:
            logger.info(f'{self.name} - 请登录')
        else:
            result = response.json()
            code = result['data']['prize_data']['card_no'] if result['msg'] == 'success' or result['msg'] == 'recently' else False
            if not code:
                logger.info(f"{self.name} - {result['data']['fail_desc1']}")
            else:
                logger.info(f'{self.name} - `{code}`')

    def main(self):
        follows = self.follow_data()
        for follow in follows:
            self.container_id = follow["containerid"]
            self.name = follow['name']
            self.sign(self.container_id)
            # 兑换
            card_ids = self.unclaimed_gift_ids()
            for card_id in card_ids:
                self.get_code(card_id)

if __name__ == "__main__":
    WeiBo().main()
