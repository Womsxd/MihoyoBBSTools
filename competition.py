import random
import time

import config
import setting
from error import CookieError
from loghelper import log
from request import http


def wait():
    time.sleep(random.randint(2, 8))


UN_FINISH = 'Unfinish'
FINISH = 'Finish'
REWARD = 'Reward'

task_sign_id = 101
task_video_id = 102
task_play_cards_id = 503


class Competition:
    def __init__(self):
        self.today_get_coins = 0
        self.today_have_get_coins = 0
        self.have_coins = 0
        self.headers = {
            'cookie': f'e_hk4e_token={config.config["competition"]["geniusinvokation"]["token"]}',
            'Referer': 'https://webstatic.mihoyo.com/',
            'Host': 'hk4e-api.mihoyo.com'
        }
        self.task_status = {
            'sign': UN_FINISH,
            'video': UN_FINISH,
            'play_cards': UN_FINISH
        }
        self.get_tasks_list()

    # 获取任务列表，用来判断做了哪些任务
    def get_tasks_list(self):
        log.info('正在获取原神赛事网站任务列表...')
        data = http.get(url=setting.adventure_task_list, headers=self.headers).json()
        if data['retcode'] == -100:
            ret_msg = '原神赛事网站token失效'
            log.warning(ret_msg)
            config.clear_cookie_competition()
            raise CookieError('Cookie expires')
        active_tasks = data['data']['active_tasks']
        task_id2task_name = {
            task_sign_id: 'sign',
            task_video_id: 'video',
            task_play_cards_id: 'play_cards'
        }
        self.today_get_coins = self.today_have_get_coins = 0
        for task in active_tasks:
            self.task_status[task_id2task_name[task['task_id']]] = task['status']
            if task['status'] == REWARD:
                self.today_have_get_coins += task['adventure_coin']
            elif task['task_id'] == task_play_cards_id and task['status'] == UN_FINISH:
                pass
            else:
                self.today_get_coins += task['adventure_coin']
        self.have_coins = data['data']['coin']
        if self.today_get_coins != 0:
            new_day = self.today_have_get_coins == 0
            log.info(f'{"新的一天，今天可以获得" if new_day else "似乎还有任务没完成，今天还能获得"}'
                     f'{self.today_get_coins}个冒险牌币')

    # 每日福利签到
    def get_sign_bonus(self):
        if self.task_status['sign'] == REWARD:
            log.info('【每日福利签到】任务已经完成过了~')
        else:
            log.info('正在做【每日福利签到】任务...')
            data = http.post(url=setting.award_adventure_task, headers=self.headers,
                             json={'task_id': task_sign_id}).json()
            if data['retcode'] == 0:
                log.info('任务成功完成')
                wait()
            else:
                log.warning(f'任务失败，原因：{data}')

    # 每日观看精彩视频
    def watch_video(self):
        if self.task_status['video'] == REWARD:
            log.info('【每日观看精彩视频】任务已经完成过了~')
        else:
            log.info('正在做【每日观看精彩视频】任务...')
            if self.task_status['video'] == UN_FINISH:
                data = http.post(url=setting.finish_adventure_task, headers=self.headers,
                                 json={'task_id': task_video_id}).json()
                if data['retcode'] != 0:
                    log.warning(f'任务失败，原因：{data}')
                    return
            data = http.post(url=setting.award_adventure_task, headers=self.headers,
                             json={'task_id': task_video_id}).json()
            if data['retcode'] == 0:
                log.info('任务成功完成')
                wait()
            else:
                log.warning(f'任务失败，原因：{data}')

    # 每周完成胜冠之试
    def play_cards(self):
        if self.task_status['play_cards'] == REWARD:
            log.info('【每周完成胜冠之试】任务已经完成过了~')
        else:
            log.info('正在做【每周完成胜冠之试】任务...')
            if self.task_status['play_cards'] == FINISH:
                data = http.post(url=setting.award_adventure_task, headers=self.headers,
                                 json={'task_id': task_play_cards_id}).json()
                if data['retcode'] == 0:
                    log.info('任务成功完成')
                    wait()
                else:
                    log.warning(f'任务失败，原因：{data}')
            else:
                log.info('你还未赢得[胜冠之试]的胜利，去猫尾酒馆打牌吧~')
                wait()

    def run_task(self):
        return_data = '原神赛事网站: '
        for retry in range(3):
            if self.task_status['sign'] == REWARD and self.task_status['video'] == REWARD \
                    and self.task_status['play_cards'] == UN_FINISH:
                return_data += '\n' + f'今天已经全部完成了！\n' \
                                      f'一共获得{self.today_have_get_coins}个冒险牌币\n目前有{self.have_coins}个冒险牌币' \
                                      f'\n本周还能获得完成[胜冠之试]的20个冒险牌币'
                log.info(f'今天已经全部完成了！一共获得{self.today_have_get_coins}个冒险牌币，'
                         f'目前有{self.have_coins}个冒险牌币')
                log.info('本周还能获得完成[胜冠之试]的20个冒险牌币')
                break
            if config.config['competition']['geniusinvokation']['checkin']:
                self.get_sign_bonus()
            if config.config['competition']['geniusinvokation']['video']:
                self.watch_video()
            if config.config['competition']['geniusinvokation']['play_cards']:
                self.play_cards()
            self.get_tasks_list()
        return_data += "\n" + f'今天已经获得{self.today_have_get_coins}个冒险牌币\n' \
                              f'还能获得{self.today_get_coins}个冒险牌币\n目前有{self.have_coins}个冒险牌币'
        log.info(f'今天已经获得{self.today_have_get_coins}个冒险牌币，'
                 f'还能获得{self.today_get_coins}个冒险牌币，目前有{self.have_coins}个冒险牌币')
        wait()
        return return_data
