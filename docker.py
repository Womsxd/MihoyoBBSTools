import os
import time
import signal
import datetime
from loghelper import log

from crontab import CronTab

time_format = "%Y-%m-%d %H:%M:%S"


def stop_me(_signo, _stack):
    log.info("Docker container has stoped....")
    exit(-1)


def main():
    signal.signal(signal.SIGINT, stop_me)
    log.info("使用DOCKER运行米游社签到")
    env = os.environ
    cron_signin = env["CRON_SIGNIN"]
    cron = CronTab(cron_signin, loop=True, random_seconds=True)

    def next_run_time():
        nt = datetime.datetime.now().strftime(time_format)
        delayt = cron.next(default_utc=False)
        nextrun = datetime.datetime.now() + datetime.timedelta(seconds=delayt)
        nextruntime = nextrun.strftime(time_format)
        log.info(f"Current running datetime: {nt}")
        log.info(f"Next run datetime: {nextruntime}")

    def sign():
        log.info("Starting signing")
        multi = env["MULTI"].upper()
        if multi == 'TRUE':
            os.system("python3 ./main_multi.py autorun")
        else:
            os.system("python3 ./main.py")

    sign()
    next_run_time()
    while True:
        ct = cron.next(default_utc=False)
        time.sleep(ct)
        sign()
        next_run_time()


if __name__ == '__main__':
    main()
