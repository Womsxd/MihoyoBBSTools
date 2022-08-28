# Server Mod
import os
#import json
import time
import config
import threading
import main as single
import main_multi as multi
from loghelper import log

time_interval = 720  # 默认签到间隔时间，单位minute(分钟)
mod = 1  # 单用户模式/自动判断


def runingtime():
    return int(time.time())


def control(time_interval, mod, event, detal):
    last_time = runingtime()
    while True:
        now_time = runingtime()
        if now_time > last_time + time_interval * 60:
            last_time = runingtime()
            if mod == 1:
                try:
                    single.main()
                except:
                    log.info("single_user start failed")

            else:
                try:
                    multi.main_multi(True)
                except:
                    log.info("multi_user start failed")
        if event.is_set():
            log.info("Stoping threading")
            break
        if (detal.is_set()):
            log.info("The Next check time is {}s".format(last_time - now_time + time_interval * 60))
        time.sleep(20)


def command(detal):
    global mod
    global time_interval
    global show
    #show = False  # 显示倒计时信息
    #if show:
    #    detal.set()
    help = "command windows\nstop:stop server\nreload:reload config and refish tiem\nsingle:test single " \
           "config\nmulit:test mulit conifg\nmod x:x is refer single or multi, 1 is single, 2 is multi\nadd " \
           "'yourcookie'\nset user attribute value: such set username(*.yaml) enable(attribute) Ture(value)\ntime " \
           "x:set interval time (minute)\nshow true/false:show the time count "
    log.info(help)
    while True:
        command = input()
        if command == "help" or command == "exit" or command == "?" or command == "":
            log.info(help)
        if command == "stop" or command == "exit":
            log.info("Stoping Server Plase Wait")
            return False

        if command == "reload":
            return True
        if command == "test":
            if mod==1:
                try:
                    single.main()
                except:
                    log.info("single_user start failed")
            else:
                try:
                    multi.main_multi(True)
                except:
                    log.info("multi_user start failed")
        if command == "single":
            try:
                single.main()
            except:
                log.info("single_user start failed")
        if command == "mulit":
            try:
                multi.main_multi(True)
            except:
                log.info("multi_user start failed")
        command = command.split(' ')
        for i in range(0, len(command)):
            if command[i] == "time":
                if len(command) == 2:
                    time_interval = int(command[1])
                    log.info("switching interval to {} minute".format(time_interval))
                    return True
            if command[i] == "mod":
                if len(command) == 2:
                    mod_new = int(command[1])
                    if mod_new > 2 or mod_new < 1:
                        log.info("error mod")
                    else:
                        mod = mod_new
                        log.info("switching mod to {}".format(mod))
                else:
                    log.info("Error Command")
            if command[i] == "show":
                if len(command) == 2:

                    if command[1] == "true":
                        detal.set()
                        log.info("switching to detail mod")

                    if command[1] == "false":
                        detal.clear()
                        log.info("switching to slient mod")


                else:
                    log.info("Error Command")
            if command[i] == "add":
                cookie = ""
                for m in range(i+1, len(command)):
                    cookie += command[m]
                log.info("adding")
                if mod == 1:
                    name = "config"
                else:
                    log.info("Plase input your config name(*.yaml):")
                    name = input()
                new_config = config.copy_config()
                new_config['account']['cookie']=cookie
                file_path = os.path.dirname(os.path.realpath(__file__)) + "/config/" + name + ".yaml"
                try:
                    config.save_config(file_path,new_config)
                    log.info("Saving OK")
                except:
                    log.info('Saving failed,plase check your file system')
                #file = open(file_path, 'w')
                #file.write(json.dumps(config))
                #file.close()
                
            if command[i] == "set":
                if len(command) == 4:
                    file_path = os.path.dirname(os.path.realpath(__file__)) + "/config/" + command[1] + ".yaml"
                    if not os.path.exists(file_path):
                        log.info("User is not exist")
                    else:
                        new_config = config.load_config(file_path)
                        #json.load(f)
                        value = command[3]
                        if command[3] == "true":
                            value = True
                        if command[3] == "false":
                            value = False
                        if command[3].isdigit():
                            value = int(command[3])
                        new_config[command[2]] = value
                        try:
                            config.save_config(file_path,new_config)
                            log.info("Saving OK")
                        except:
                            log.info('Saving failed,plase check your file system')
                        #file = open(file_path, 'w')
                        #file.write(json.dumps(new_conifg))
                        #file.close()
    return True


if __name__ == '__main__':
    log.info('Running in Server Mod')
    file_path = os.path.dirname(os.path.realpath(__file__)) + "/config/config.yaml"
    
    if os.path.exists(file_path):
        mod = 1
    else:
        mod = 2

    while True:
        log.info("switching to mod {}".format(mod))
        t1_stop = threading.Event()
        detal = threading.Event()
        thread1 = threading.Thread(name='time_check', target=control, args=(time_interval, mod, t1_stop, detal))
        thread1.start()
        try:
            if command(detal):
                t1_stop.set()
                continue
            else:
                t1_stop.set()
                break
        except:
            t1_stop.set()
            continue
