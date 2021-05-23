import login
import config
import setting
import mihoyobbs

#初始化，加载配置
config.Load_config()
#检测参数是否齐全，如果缺少就进行登入操作
if (config.mihoyobbs_Login_ticket == "" or config.mihoyobbs_Stuid == "" or config.mihoyobbs_Stoken == ""):
    #登入
    login.login()
#获取要使用的BBS列表
#判断是否开启bbs_Singin_multi
if (config.mihoyobbs["bbs_Singin_multi"] == True):
    for i in setting.mihoyobbs_List:
        if (int(i["id"]) in config.mihoyobbs["bbs_Singin_multi_list"]):
            setting.mihoyobbs_List_Use.append(i)
else:
    #关闭bbs_Singin_multi后只签到大别墅
    for i in setting.mihoyobbs_List:
        if (int(i["id"]) == 5):
            setting.mihoyobbs_List_Use.append(i)
#米游社签到
if(config.mihoyobbs["bbs_Gobal"] == True):
    bbs = mihoyobbs.mihoyobbs()
    if (config.mihoyobbs["bbs_Singin"] == True):
        bbs.Singin()
    if (config.mihoyobbs["bbs_Read_posts"] == True):
        bbs.Readposts()
    if (config.mihoyobbs["bbs_Like_posts"] == True):
        bbs.Likeposts()
    if (config.mihoyobbs["bbs_Share"] == True):
        bbs.Share()
