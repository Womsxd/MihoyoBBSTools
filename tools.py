import uuid
import time
import config
import random
import string
import logging
import hashlib
import setting

#Log输出
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
    datefmt='%Y-%m-%dT%H:%M:%S')

log = logger = logging

#md5计算
def MD5(text:str) -> str:
    md5 = hashlib.md5()
    md5.update(text.encode())
    return (md5.hexdigest())

#随机文本
def Random_text(num:int) -> str:
    return(''.join(random.sample(string.ascii_lowercase + string.digits, num)))

#时间戳
def Timestamp() -> int:
    return(int(time.time()))

#获取请求Header里的DS 当web为true则生成网页端的DS
def Get_ds(web:bool, web_old:bool) -> str:
    if(web == True):
        if(web_old == True):
            n = setting.mihoyobbs_Salt_web_old
        else:
            n = setting.mihoyobbs_Salt_web
    else:
        n = setting.mihoyobbs_Salt
    i = str(Timestamp())
    r = Random_text(6)
    c = MD5("salt=" + n + "&t=" + i + "&r=" + r)
    return (i + "," + r + "," + c)

#生成一个device id
def Get_deviceid() -> str:
    return (str(uuid.uuid3(uuid.NAMESPACE_URL, config.mihoyobbs_Cookies)).replace(
                '-', '').upper())

#获取明天早晨0点的时间戳
def Nextday() -> int:
    now_time = int(time.time())
    nextday_time = now_time - now_time % 86400 + time.timezone + 86400
    return (nextday_time)