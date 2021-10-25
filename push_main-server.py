import sys
import time
import random
import subprocess
from request import http

SendKey = ""
send_Url = f"https://sctapi.ftqq.com/{SendKey}.send"

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
            "title": "米游社脚本执行出错！",
            "desp": "这里是运行相关日志：\r\n" + opt_info
        }
    )
else:
    http.post(
        url=send_Url,
        data={
            "title": "米游社脚本执行成功",
            "desp": "这里是运行相关日志：\r\n" + opt_info
        }
    )
    print("OK!")
exit(0)
