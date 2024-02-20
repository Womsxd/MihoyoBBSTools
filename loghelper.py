import os
import logging

# Log输出，这里提供了自定义logging输出的机会，只需要创建一个logging.ini并且写入配置文件即可自定义输出
file_path = os.path.dirname(os.path.realpath(__file__)) + "/config/logging.ini"
if os.path.exists(file_path):
    import logging.config

    logging.config.fileConfig(file_path,encoding='utf-8')
    log = logging.getLogger("AutoMihoyoBBS")
else:
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(levelname)s %(message)s',
        datefmt='%Y-%m-%dT%H:%M:%S')
    log = logging

# 获取httpx的日志记录器，并将其级别设置为CRITICAL，让日志不再输出httpx的相关日志
httpx_log = logging.getLogger("httpx")
httpx_log.setLevel(logging.CRITICAL)
