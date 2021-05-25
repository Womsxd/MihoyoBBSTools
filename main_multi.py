import os
import main
import time
import tools
import config

#搜索配置文件
def Fund_config() ->list:
    file_Name=[]
    for files in os.listdir(config.path):
        if os.path.splitext(files)[1] == '.json':
            file_Name.append(files)
    return (file_Name)

def main_multi():
    tools.log.info("AutoMihoyoBBS Multi User mode")
    tools.log.info("正在搜索配置文件！")
    config_List = Fund_config()
    tools.log.info(f"已搜索到{len(config_List)}个配置文件，请确认是否无多余文件！\r\n{config_List}")
    input("请输入回车继续，需要重新搜索配置文件请Ctrl+C退出脚本")
    for i in iter(config_List):
        tools.log.info(f"正在执行{i}")
        config.config_Path= f"{config.path}/{i}"
        main.main()
        tools.log.info(f"{i}执行完毕")
        time.sleep(2)

if __name__ == "__main__":
    main_multi()
pass