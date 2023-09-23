import os
import logging

# Log输出，这里提供了自定义logging输出的机会，只需要创建一个logging.ini并且写入配置文件即可自定义输出
file_path = os.path.dirname(os.path.realpath(__file__)) + "/config/logging.ini"
if os.path.exists(file_path):
    import logging.config

    logging.config.fileConfig(file_path)
    log = logging.getLogger("AutoMihoyoBBS")
else:
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(levelname)s %(message)s',
        datefmt='%Y-%m-%dT%H:%M:%S')
    log = logging

# 获取httpx的日志记录器，并将其级别设置为DEBUG，让httpx只在debug下输出日志
httpx_log = logging.getLogger("httpx")
httpx_log.setLevel(logging.DEBUG)
