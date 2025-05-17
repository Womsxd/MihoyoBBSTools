import time
import random
import config
from request import get_new_session
from loghelper import log
from datetime import datetime


def genshin_mizone():
    client = get_new_session()
    base_url = 'https://act-hk4e-api.mihoyo.com/event/e20250430linkdrink/'
    task_url = f'{base_url}index'
    task_done_url = f'{base_url}claim_task'
    headers = {
        'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/135.0.0.0 Safari/537.36",
        'Accept-Encoding': "gzip, deflate",
        'origin': "https://act.mihoyo.com",
        'referer': "https://act.mihoyo.com/",
        'accept-language': "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
        'Cookie': config.config['account']['cookie']
    }

    def get_task_data() -> dict:
        resp = client.get(task_url, params={"lang": "zh-cn", "game_biz": "hk4e_cn"}, headers=headers)
        if resp.status_code != 200:
            raise Exception(f'获取任务数据失败: {resp.status_code}')
        data = resp.json()
        if data['retcode'] != 0:
            raise Exception(f'获取任务数据失败: {data["message"]}')
        return data['data']

    def done_task(task_id: int):
        resp = client.post(task_done_url, json={"task_id": task_id}, headers=headers)
        if resp.status_code != 200:
            raise Exception(f'完成任务失败: {resp.status_code}')
        data = resp.json()
        if data['retcode'] != 0:
            raise Exception(f'完成任务失败: {data["message"]}')
        return True

    # 如果当前系统日期大于2025-10-31 则跳过
    if datetime.now().date() > datetime(2025, 10, 31).date():
        log.info("当前系统日期大于2025-10-31，跳过执行任务")
        return

    count = 0
    task_data = get_task_data()
    time.sleep(random.randint(2, 5))
    for task in task_data['task_infos']:
        if task['status'] == "TS_DONE":
            done_task(task['task_id'])
            count += 1
            if count == 4:
                break
            time.sleep(random.randint(1, 3))
            continue
        elif task['status'] == "Task_Limit":
            break


def run_task():
    """根据配置执行网页活动任务"""
    if not config.config.get('web_activity', {}).get('enable', False):
        log.info("网页活动功能未启用")
        return
    
    activities = config.config.get('web_activity', {}).get('activities', [])
    if not activities:
        log.info("未配置需要执行的网页活动")
        return
    
    log.info(f"开始执行网页活动: {activities}")
    
    for activity in activities:
        try:
            # 检查是否有对应的函数
            func = globals().get(activity)
            if func and callable(func):
                log.info(f"开始执行活动: {activity}")
                func()
                log.info(f"活动 {activity} 执行完成")
            else:
                log.warning(f"未找到活动函数: {activity}")
        except Exception as e:
            log.error(f"执行活动 {activity} 时出错: {str(e)}")
