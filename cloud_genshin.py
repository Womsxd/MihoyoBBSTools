import setting
from request import http
import tools
import config
from loghelper import log



class cloud_ys():
    def __init__(self,token) -> None:
        self.headers = {
            'x-rpc-combo_token': token,
            'x-rpc-client_type': setting.mihoyobbs_Client_type,
            'x-rpc-app_version': setting.cloudgenshin_Version,
            'x-rpc-sys_version': '12',  # Previous version need to convert the type of this var
            'x-rpc-channel': 'mihoyo',
            'x-rpc-device_id': tools.get_device_id(),
            'x-rpc-device_name': 'Xiaomi M2012K11AC',
            'x-rpc-device_model': 'M2012K11AC',
            'x-rpc-app_id': '1953439974',
            'Referer': 'https://app.mihoyo.com',
            'Host': 'api-cloudgame.mihoyo.com',
            'Connection': 'Keep-Alive',
            'Accept-Encoding': 'gzip',
            'User-Agent': 'okhttp/4.9.0'
        }

    def Sgin(self):
        req = http.get(url=setting.Cloud_Ys_Sgin,headers=self.headers).json()
        try:
            jg = req['data']['list'][0]['msg']
            if "每日登录奖励" in jg:
                log.info("云原神签到成功")
                data = "云原神签到成功"
        except IndexError:
            log.warning("云原神签到失败或重复签到")
            data = "云原神签到失败或重复签到"
        except Exception as er:
            log.warning(f"云原神签到失败,出现了错误:{er}")
            data = f"云原神签到失败,出现了错误:{er}"
        reqs = http.get(url=setting.Cloud_ys_Inquire,headers=self.headers).json()
        nr = (f"\n你当前拥有免费时长 {reqs['data']['free_time']['free_time']} 分钟，畅玩卡状态为 {reqs['data']['play_card']['short_msg']}，拥有米云币 {reqs['data']['coin']['coin_num']} 枚")
        data = data + nr
        return data
