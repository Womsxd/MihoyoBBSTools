import time
import httpx
import tools
import config
import random
import setting


class mihoyobbs:
    def __init__(self):
        self.headers = {
            "DS": tools.Get_ds(web=False, web_old=False),
            "cookie": f"stuid={config.mihoyobbs_Stuid};stoken={config.mihoyobbs_Stoken}",
            "x-rpc-client_type": setting.mihoyobbs_Client_type,
            "x-rpc-app_version": setting.mihoyobbs_Version,
            "x-rpc-sys_version": "6.0.1",
            "x-rpc-channel": "mihoyo",
            "x-rpc-device_id": tools.Random_text(20) + tools.Random_text(12),
            "x-rpc-device_name": tools.Random_text(random.randint(1, 10)),
            "x-rpc-device_model": "Mi 10",
            "Referer": "https://app.mihoyo.com",
            "Host": "bbs-api.mihoyo.com",
            "User-Agent": "okhttp/4.8.0"
        }
        self.postsList = self.Getlist()
    #进行签到操作
    def Singin(self):
        tools.log.info("正在签到......")
        for i in setting.mihoyobbs_List_Use:
            req = httpx.post(url=setting.signUrl.format(i["id"]), data="" ,headers=self.headers)
            data = req.json()
            if ("err" not in data["message"]):
                tools.log.info(str(i["name"]+ data["message"]))
                time.sleep(2)
            else:
                tools.log.info("签到失败，你的cookie可能已过期，请重新设置cookie。")
                config.Clear_cookies()
                exit()
    #获取要帖子列表
    def Getlist(self) -> list:
        temp_List = []
        tools.log.info("正在获取帖子列表......")
        for i in setting.mihoyobbs_List_Use:
            req = httpx.get(url=setting.listUrl.format(i["forumId"]), headers=self.headers)
            data = req.json()
            for n in range(10):
                temp_List.append([data["data"]["list"][n]["post"]["post_id"], data["data"]["list"][n]["post"]["subject"]])
            tools.log.info("已获取{}个帖子".format(len(temp_List)))
            time.sleep(2)
        return (temp_List)
    #看帖子
    def Readposts(self):
        tools.log.info("正在看帖......")
        for i in range(3):
            req = httpx.get(url=setting.detailUrl.format(self.postsList[i][0]), headers=self.headers)
            data = req.json()
            if data["message"] == "OK":
                tools.log.info("看帖：{} 成功".format(self.postsList[i][1]))
            time.sleep(2)
    #点赞
    def Likeposts(self):
        tools.log.info("正在点赞......")
        for i in range(5):
            req = httpx.post(url=setting.likeUrl, headers=self.headers,
                    json={"post_id": self.postsList[i][0], "is_cancel": False})
            data = req.json()
            if (data["message"] == "OK"):
                tools.log.info("点赞：{} 成功".format(self.postsList[i][1]))
            #判断取消点赞是否打开
            if (config.mihoyobbs["bbs_Unlike"] == True):
                req = httpx.post(url=setting.likeUrl, headers=self.headers,
                    json={"post_id": self.postsList[i][0], "is_cancel": True})
                data = req.json()
                if (data["message"] == "OK"):
                    tools.log.info("取消点赞：{} 成功".format(self.postsList[i][1]))
            time.sleep(2)
    def Share(self):
        tools.log.info("正在分享......")
        req = httpx.get(url=setting.shareUrl.format(self.postsList[0][0]), cookies=self.Cookie, headers=self.headers)
        data = req.json()
        if data["message"] == "OK":
            tools.log.info("分享：{} 成功".format(self.postsList[0][1]))