import httpx
import tools
import config
import setting

class genshin:
    def __init__(self) -> None:
        self.headers = {
                'Accept': 'application/json, text/plain, */*',
                'DS': tools.Get_ds(web=True, web_old=True),
                'Origin': 'https://webstatic.mihoyo.com',
                'x-rpc-app_version': setting.mihoyobbs_Version_old,
                'User-Agent': 'Mozilla/5.0 (Linux; Android 9; Unspecified Device) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/39.0.0.0 Mobile Safari/537.36 miHoYoBBS/2.3.0',
                'x-rpc-client_type': setting.mihoyobbs_Client_type_web,
                'Referer': 'https://webstatic.mihoyo.com/bbs/event/signin-ys/index.html?bbs_auth_required=true&act_id=e202009291139501&utm_source=bbs&utm_medium=mys&utm_campaign=icon',
                'Accept-Encoding': 'gzip, deflate',
                'Accept-Language': 'zh-CN,en-US;q=0.8',
                'X-Requested-With': 'com.mihoyo.hyperion',
                "Cookie": config.mihoyobbs_Cookies,
                'x-rpc-device_id': tools.Get_driveid()
            }
        self.acc_List = self.Getacc_list()
        self.sing_Give = self.Get_singgive()
    #获取绑定的账号列表
    def Getacc_list(self) -> list:
        temp_List = []
        req = httpx.get(setting.genshin_Accinfo_url, headers=self.headers)
        data = req.json()
        if (data["retcode"] != 0):
            tools.log.warn("获取账号列表失败！")
            exit()
        for i in data["data"]["list"]:
            temp_List.append([i["nickname"], i["game_uid"], i["region"]])
        return (temp_List)
    #获取已经签到奖励列表
    def Get_singgive(self) -> list:
        req = httpx.get(setting.genshin_Singlisturl.format(setting.genshin_Act_id),headers=self.headers)
        data = req.json()
        if (data["retcode"] != 0):
            tools.log.warn("获取签到奖励列表失败")
            print (req.text)
            exit()
        return (data["data"]["awards"])
    #判断签到
    def Is_sing(self, region:str, uid:str):
        req = httpx.get(setting.genshin_Is_singurl.format(setting.genshin_Act_id, region, uid), headers=self.headers)
        data = req.json()
        if (data["retcode"] != 0):
            tools.log.warn("获取账号签到信息失败！")
            print (req.text)
            exit()
        return (data["data"])
    #签到
    def Get_item(self, raw_data:dict) ->str:
        temp_Name = raw_data["name"]
        temp_Cnt = raw_data["cnt"]
        return (f"{temp_Name}x{temp_Cnt}")

    def Sing_acc(self):
        for i in self.acc_List:
            is_data = self.Is_sing(region = i[2], uid = i[1])
            if (is_data["first_bind"] == True):
                tools.log.warn(f"旅行者{i[0]}是第一次绑定米游社，请先手动签到一次")
            else:
                sing_Days = is_data["total_sign_day"]
                if (is_data["is_sign"] == True):
                    tools.log.info(f"旅行者{i[0]}今天已经签到过了~\r\n今天获得的奖励是{self.Get_item(self.sing_Give[sing_Days])}")
                else:
                    req = httpx.post(url=setting.genshin_Singurl, headers=self.headers,
                            json={'act_id': setting.genshin_Act_id, 'region': i[2], 'uid': i[1]})
                    data = req.json()
                    if (data["retcode"] == 0):
                        tools.log.info(f"旅行者{i[0]}签到成功~\r\n今天获得的奖励是{self.Get_item(self.sing_Give[sing_Days + 1])}")
                    elif (data["retcode"] == -5003):
                        tools.log.info(f"旅行者{i[0]}今天已经签到过了~\r\n今天获得的奖励是{self.Get_item(self.sing_Give[sing_Days])}")
                    else:
                        tools.log.warn("账号签到失败！")
                        print (req.text)
