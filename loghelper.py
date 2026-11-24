import os
import logging
import logging.config
from typing import List


class PushMessageCollector:
    """收集需要推送给用户的消息，由 push 模块统一发送"""

    def __init__(self) -> None:
        self._messages: List[str] = []

    def add(self, message: str) -> None:
        self._messages.append(message)

    def drain(self) -> str:
        message = "\n".join(self._messages)
        self.clear()
        return message

    def clear(self) -> None:
        self._messages.clear()


push_message = PushMessageCollector()


class MihoyoBBSLogger(logging.getLoggerClass()):
    """在标准 Logger 上增加 push 方法，输出日志的同时收集为推送消息"""

    def push(self, msg: str, *args, level: int = logging.INFO, **kwargs) -> None:
        self.log(level, msg, *args, **kwargs)
        if args:
            try:
                msg = msg % args
            except (TypeError, ValueError):
                msg = " ".join([str(msg), *map(str, args)])
        push_message.add(msg)


logging.setLoggerClass(MihoyoBBSLogger)

# Log输出，这里提供了自定义logging输出的机会，只需要创建一个logging.ini并且写入配置文件即可自定义输出
file_path = os.path.dirname(os.path.realpath(__file__)) + "/config/logging.ini"
if os.path.exists(file_path):
    logging.config.fileConfig(file_path, encoding='utf-8')
else:
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(levelname)s %(message)s',
        datefmt='%Y-%m-%dT%H:%M:%S')

log = logging.getLogger("AutoMihoyoBBS")


def clear_push_message() -> None:
    """开始新一轮任务前清空已收集的推送消息"""
    push_message.clear()


def collect_push_message(message: str) -> None:
    """仅收集推送消息，不重复输出日志（消息生成时已输出过）"""
    push_message.add(message)


def drain_push_message() -> str:
    """取出并清空已收集的推送消息"""
    return push_message.drain()


# 获取httpx的日志记录器，并将其级别设置为CRITICAL，让日志不再输出httpx的相关日志
httpx_log = logging.getLogger("httpx")
httpx_log.setLevel(logging.CRITICAL)
