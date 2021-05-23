import time
import httpx
import tools
import config
import random
import setting

class genshin:
    def __init__(self) -> None:
        self.headers = {
                'Accept': 'application/json, text/plain, */*',
                'DS': tools.Get_ds(web=True, web_old=True),
                'Origin': 'https://webstatic.mihoyo.com',
                'x-rpc-app_version': setting.mihoyobbs_Version_old,
                'User-Agent': 'Mozilla/5.0 (Linux; Android 9; Unspecified Device) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/39.0.0.0 Mobile Safari/537.36 miHoYoBBS/2.2.0',
                'x-rpc-client_type': setting.mihoyobbs_Client_type_web,
                'Referer': 'https://webstatic.mihoyo.com/bbs/event/signin-ys/index.html?bbs_auth_required=true&act_id=e202009291139501&utm_source=bbs&utm_medium=mys&utm_campaign=icon',
                'Accept-Encoding': 'gzip, deflate',
                'Accept-Language': 'zh-CN,en-US;q=0.8',
                'X-Requested-With': 'com.mihoyo.hyperion',
                "Cookie": config.mihoyobbs_Cookies
            }
        self.acc_List = self.Getacc_list()
    #获取绑定的账号列表
    def Getacc_list(self) -> list:
        temp_List = []
        req = httpx.get(setting.accinfo_Url, headers=self.headers)
        data = req.json()
        if (data["rercode"] != 0):
            tools.log.warn("获取账号列表失败！")
            exit()
        for i in data["data"]["list"]:
            temp_List.append([i["nickname"], i["game_uid"], i["region"]])
        return (temp_List)
