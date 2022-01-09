import sys
import time
import random
import subprocess
from request import http

SendKey = ""
send_Url = "http://www.pushplus.plus/send"

python_Path = sys.executable

run_ShellCommand = python_Path + " main_multi.py autorun"

for i in range(2):
    opt_id, opt_info = subprocess.getstatusoutput(run_ShellCommand)
    if opt_id == 0:
        break
    time.sleep(random.randint(30, 70))

if opt_id != 0:
    print("Error!")
    http.post(
        url=send_Url,
        data={
            "token": SendKey,
            "title": "「米游社-签到」Error!",
            "content": opt_info.split()[-1] + "\n这里是运行相关日志：\r\n" + opt_info,
        }
    )
else:
    print("OK!")
    http.post(
        url=send_Url,
        data={
            "token": SendKey,
            "title": "「米游社-签到」OK!",
            "content": opt_info.split()[-1] + "\n这里是运行相关日志：\r\n" + opt_info,
        }
    )
exit(0)
