import login
import tools
import config
import genshin
import setting
import mihoyobbs
import honkai3rd

def main():
    #初始化，加载配置
    config.Load_config()
    if config.enable_Config == True:
    #检测参数是否齐全，如果缺少就进行登入操作
        if config.mihoyobbs_Login_ticket == "" or config.mihoyobbs_Stuid == "" or config.mihoyobbs_Stoken == "":
        #登入
            login.login()
        #获取要使用的BBS列表,#判断是否开启bbs_Singin_multi
        if config.mihoyobbs["bbs_Singin_multi"] == True:
            #速度快，但是无法设置主社区，主社区默认为第一个
            '''
            for i in setting.mihoyobbs_List:
                if int(i["id"]) in config.mihoyobbs["bbs_Singin_multi_list"]:
                    setting.mihoyobbs_List_Use.append(i)
            '''
            #用这里的方案可以实现当让id在第一个的时候为主社区
            for i in config.mihoyobbs["bbs_Singin_multi_list"]:
                for i2 in setting.mihoyobbs_List:
                    if i == int(i2["id"]):
                        setting.mihoyobbs_List_Use.append(i2)
        else:
            #关闭bbs_Singin_multi后只签到大别墅
            for i in setting.mihoyobbs_List:
                if int(i["id"]) == 5:
                    setting.mihoyobbs_List_Use.append(i)
        #米游社签到
        if config.mihoyobbs["bbs_Global"] == True:
            bbs = mihoyobbs.mihoyobbs()
            if config.mihoyobbs["bbs_Singin"] == True:
                bbs.Singin()
            if config.mihoyobbs["bbs_Read_posts"] == True:
                bbs.Readposts()
            if config.mihoyobbs["bbs_Like_posts"] == True:
                bbs.Likeposts()
            if config.mihoyobbs["bbs_Share"] == True:
                bbs.Share()
            tools.log.info(f"今天还能获得{mihoyobbs.Today_getcoins}个米游币，目前有{mihoyobbs.Have_coins}个米游币")
        else:
            tools.log.info("米游社功能未启用！")
        #原神签到
        if(config.genshin_AutoSingin == True):
            tools.log.info("正在进行原神签到")
            genshin_Help = genshin.genshin()
            genshin_Help.Sing_acc()
        else:
            tools.log.info("原神签到功能未启用！")
        #崩坏3签到
        if config.honkai3rd_AutoSing == True:
            tools.log.info("正在进行崩坏3签到")
            honkai3rd_Help = honkai3rd.honkai3rd()
            honkai3rd_Help.Sing_acc()
        else:
            tools.log.info("崩坏3签到功能未启用！")
    else:
        tools.log.warn ("Config未启用！")

if __name__ == "__main__":
    main()
pass