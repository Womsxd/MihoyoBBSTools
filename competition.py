import re
import time
import random

import config
import account
import setting
from error import CookieError
from loghelper import log
from request import get_new_session


def cookie_get_hk4e_token(cookies: str) -> str:
    """
    从 cookie 中获取 hk4e_token
    :return: hk4e_token
    """
    match = re.search(r"e_hk4e_token=([^;]+)", cookies)
    if match:
        e_hk4e_token = match.group(1)
        return e_hk4e_token
    else:
        return ''


class GeniusInvokation:
    http = get_new_session()
    task_list = {
        # finish是False证明reward一定是False，finish是True不一定是reward不一定是true
        101: {'task_id': 101, 'task_name': '每日签到', 'finish': False, 'reward': False},
        503: {'task_id': 503, 'task_name': '每周完成冠胜之试', 'finish': False, 'reward': False},
        504: {'task_id': 504, 'task_name': '每周完成10场匹配', 'finish': False, 'reward': False},
        505: {'task_id': 505, 'task_name': '每周获得3场匹配胜利', 'finish': False, 'reward': False}
    }

    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/121.0.0.0 Safari/537.36', 'Accept': 'application/json, text/plain, */*',
            'Origin': 'https://webstatic.mihoyo.com', 'Referer': 'https://webstatic.mihoyo.com/',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Cookie': ''}
        # self.user_info = self.get_info()
        self.user_info = self.get_hk4e_token()
        if self.user_info is not None:
            self.headers['x-rpc-cover-session'] = self.user_info['game_uid']
            self.params = {'badge_uid': self.user_info['game_uid'], 'badge_region': self.user_info['region'],
                           'game_biz': self.user_info['game_biz'], 'lang': 'zh-cn'}

    def set_hk4e_token(self, hk4e_token: str):
        """
        设置hk4e token
        :return:
        """
        self.headers['Cookie'] = f'e_hk4e_token={hk4e_token}'

    def get_info(self):
        """
        获取账号信息
        :return:
        """
        response = self.http.get(setting.hk4e_token_get_info_url,
                                 params={'game_biz': 'hk4e_cn', 'lang': 'zh-cn', 'ts': int(time.time() * 1000)},
                                 headers=self.headers)
        if response.status_code != 200:
            return None
        data = response.json()
        if data['retcode'] == 0:
            user_data = data['data']
            return {"nickname": user_data['nickname'], "game_uid": user_data['game_uid'],
                    "region": user_data['region'], "game_biz": f'{user_data["game"]}_cn'}
        elif data['retcode'] == -100:
            log.warning('hk4e Token 过期')
            return self.get_hk4e_token()
        return None

    def get_account_list(self, headers) -> list:
        try:
            account_list = account.get_account_list('hk4e_cn', headers)
        except CookieError:
            log.warning('cookie过期')
            raise CookieError("BBS Cookie Error")
        return account_list

    def get_hk4e_token(self):
        """
        获取hk4e token
        :return:
        """
        log.info('获取hk4e token')
        headers = self.headers.copy()
        headers['Cookie'] = config.config['account']['cookie']
        account_list = self.get_account_list(headers)
        response = self.http.post(setting.get_hk4e_token_url,
                                  json={'game_biz': 'hk4e_cn', 'lang': 'zh-cn',
                                        'region': account_list[0][2], 'uid': account_list[0][1]},
                                  headers=headers)
        if response.status_code != 200:
            return None
        data = response.json()
        if data['retcode'] == 0:
            log.info('获取hk4e token成功')
            self.set_hk4e_token(cookie_get_hk4e_token(''.join(response.headers['Set-Cookie'])))
            user_data = data['data']
            return {"nickname": user_data['nickname'], "game_uid": user_data['game_uid'],
                    "region": user_data['region'], "game_biz": f'{user_data["game"]}_cn'}
        return None

    def get_task_list(self):
        """
        获取任务列表
        :return:
        """
        response = self.http.get(setting.genius_invokation_task_url, params=self.params, headers=self.headers)
        if response.status_code != 200:
            return None
        data = response.json()
        if data['retcode'] != 0:
            return None
        for i in data['data']['active_tasks']:
            task = self.task_list.get(i['task_id'])
            if task is None:
                continue
            if i['status'] == 'Reward':
                task['reward'] = True
            elif i['status'] == 'Finish':
                task['finish'] = True

    def get_award(self, task_id: int):
        """
        领取领取奖励
        :return:
        """
        request = self.http.post(setting.genius_invokation_get_award_url, params=self.params,
                                 json={"task_id": task_id}, headers=self.headers)
        if request.status_code != 200:
            return None
        data = request.json()
        # -521040 代表已经领取过奖励了
        if data['retcode'] == 0 or data['retcode'] == -521040:
            return True
        return None

    def checkin(self):
        """
        签到

        :return:
        """
        task_info = self.task_list.get(101)
        if task_info['reward']:
            return '已经签到过了'
        if not task_info['finish']:
            return '无法获取每日签到奖励'
        if self.get_award(task_info['task_id']):
            task_info['reward'] = True
            log.info('成功完成每日签到')
            return '成功签到'
        return f'无法进行签到'

    def week_task(self, task_ids: list):
        """
        每周打牌任务
        """

        def do_task(task: int):
            task_info = self.task_list.get(task)
            if task_info['reward']:
                return ''  # 领取后了应该不需要提示了
            if not task_info['finish']:
                return f'每周任务:{task_info["task_name"]} 还未完成'
            if self.get_award(task_info['task_id']):
                task_info['reward'] = True
                return f'成功领取每周任务:{task_info["task_name"]} 奖励'
            return f'无法领取 {task_info["task_name"]} 奖励'

        results = ""
        for task_id in task_ids:
            result = do_task(task_id)
            log.info(result)
            results += f'{result}\n'
        return results

    def run_task(self):
        """
        执行签到任务
        :return:
        """
        time.sleep(random.randint(3, 8))
        log.info("七圣召唤赛事任务开始")
        result = '\n七圣召唤比赛: '
        if not self.user_info:
            log.warning("账号没有绑定任何原神账号！")
            result += "账号没有绑定任何原神账号！"
            return result
        self.get_task_list()
        time.sleep(random.randint(3, 8))
        task_config = config.config['competition']['genius_invokation']
        if task_config['checkin']:
            result += f'\n{self.checkin()}'
            time.sleep(random.randint(3, 8))
        if task_config['weekly']:
            result += f'\n{self.week_task([503,504,505])}'
        log.info('七圣召唤赛事任务执行完毕')
        return result


def run_task():
    result = ''
    if config.config['competition']['genius_invokation']['enable']:
        genius_invokation = GeniusInvokation()
        result += genius_invokation.run_task()
    return result
