import time
import login
import tools
import config
import random
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
            time.sleep(random.randint(2, 8))
        #获取要使用的BBS列表,#判断是否开启bbs_Signin_multi
        if config.mihoyobbs["bbs_Signin_multi"] == True:
            #速度快，但是无法设置主社区，主社区默认为第一个
            '''
            for i in setting.mihoyobbs_List:
                if int(i["id"]) in config.mihoyobbs["bbs_Signin_multi_list"]:
                    setting.mihoyobbs_List_Use.append(i)
            '''
            #用这里的方案可以实现当让id在第一个的时候为主社区
            for i in config.mihoyobbs["bbs_Signin_multi_list"]:
                for i2 in setting.mihoyobbs_List:
                    if i == int(i2["id"]):
                        setting.mihoyobbs_List_Use.append(i2)
        else:
            #关闭bbs_Signin_multi后只签到大别墅
            for i in setting.mihoyobbs_List:
                if int(i["id"]) == 5:
                    setting.mihoyobbs_List_Use.append(i)
        #米游社签到
        if config.mihoyobbs["bbs_Global"] == True:
            bbs = mihoyobbs.mihoyobbs()
            if bbs.Task_do["bbs_Sign"] and bbs.Task_do["bbs_Read_posts"] and bbs.Task_do["bbs_Like_posts"] and bbs.Task_do["bbs_Share"]:
                tools.log.info(f"今天已经全部完成了！一共获得{mihoyobbs.Today_have_getcoins}个米游币，目前有{mihoyobbs.Have_coins}个米游币")
            else: 
                if config.mihoyobbs["bbs_Signin"] == True:
                    bbs.Signin()
                if config.mihoyobbs["bbs_Read_posts"] == True:
                    bbs.Readposts()
                if config.mihoyobbs["bbs_Like_posts"] == True:
                    bbs.Likeposts()
                if config.mihoyobbs["bbs_Share"] == True:
                    bbs.Share()
                bbs.Get_taskslist()
                tools.log.info(f"今天已经获得{mihoyobbs.Today_have_getcoins}个米游币，还能获得{mihoyobbs.Today_getcoins}个米游币，目前有{mihoyobbs.Have_coins}个米游币")
                time.sleep(random.randint(2, 8))
        else:
            tools.log.info("米游社功能未启用！")
        #原神签到
        if(config.genshin_Auto_sign == True):
            tools.log.info("正在进行原神签到")
            genshin_Help = genshin.genshin()
            genshin_Help.Sign_acc()
            time.sleep(random.randint(2, 8))
        else:
            tools.log.info("原神签到功能未启用！")
        #崩坏3签到
        if config.honkai3rd_Auto_sign == True:
            tools.log.info("正在进行崩坏3签到")
            honkai3rd_Help = honkai3rd.honkai3rd()
            honkai3rd_Help.Sign_acc()
        else:
            tools.log.info("崩坏3签到功能未启用！")
    else:
        tools.log.warn ("Config未启用！")

if __name__ == "__main__":
    main()
pass