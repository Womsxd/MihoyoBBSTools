import os
import sys
import main
import time
import tools
import config
import random
import setting

#搜索配置文件
def Fund_config() ->list:
    file_Name=[]
    for files in os.listdir(config.path):
        if os.path.splitext(files)[1] == '.json':
            file_Name.append(files)
    return (file_Name)

def main_multi(autorun:bool):
    tools.log.info("AutoMihoyoBBS Multi User mode")
    tools.log.info("正在搜索配置文件！")
    config_List = Fund_config()
    if len(config_List) == 0:
        tools.log.warn("未检测到配置文件，请确认config文件夹存在.json后缀名的配置文件！")
        exit(1)
    if autorun:
        tools.log.info(f"已搜索到{len(config_List)}个配置文件，正在开始执行！")
    else:
        tools.log.info(f"已搜索到{len(config_List)}个配置文件，请确认是否无多余文件！\r\n{config_List}")
        try:
            input("请输入回车继续，需要重新搜索配置文件请Ctrl+C退出脚本")
        except:
            exit(0)
    for i in iter(config_List):
        tools.log.info(f"正在执行{i}")
        setting.mihoyobbs_List_Use = []
        config.config_Path= f"{config.path}/{i}"
        main.main()
        tools.log.info(f"{i}执行完毕")
        time.sleep(random.randint(3, 10))

if __name__ == "__main__":
    if len(sys.argv) >= 2 and sys.argv[1] == "autorun":
        autorun = True
    else:
        autorun = False
    main_multi(autorun)
    exit(0)
pass