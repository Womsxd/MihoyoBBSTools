# 米游社的Salt
# java提取，会跟随版本更新
mihoyobbs_salt = "pIlzNr5SAZhdnFW8ZxauW8UlxRdZc45r"
mihoyobbs_salt_web = "0wr0OpH2BNuekYrfeRwkiDdshvt10cTY"
# so提取 一般不会变
mihoyobbs_salt_x4 = "xV8v4Qu54lUKrEYFZkJhB8cuOh9Asafs"
mihoyobbs_salt_x6 = "t0qEgfub6cvueAPgR5m9aQWWVciEer7v"
# 部分接口要带
mihoyobbs_verify_key = "bll8iq97cem8"
# 米游社的版本
mihoyobbs_version = "2.62.2"  # Salt和Version相互对应
# 米游社的客户端类型
mihoyobbs_Client_type = "2"  # 1为ios 2为安卓
mihoyobbs_Client_type_web = "5"  # 4为pc web 5为mobile web
# 云原神相关数据
cloudgenshin_Version = "4.0.0"

# 米游社的分区列表
mihoyobbs_List = [{
    "id": "1",
    "forumId": "1",
    "name": "崩坏3",
    "url": "https://bbs.mihoyo.com/bh3/"
}, {
    "id": "2",
    "forumId": "26",
    "name": "原神",
    "url": "https://bbs.mihoyo.com/ys/"
}, {
    "id": "3",
    "forumId": "30",
    "name": "崩坏2",
    "url": "https://bbs.mihoyo.com/bh2/"
}, {
    "id": "4",
    "forumId": "37",
    "name": "未定事件簿",
    "url": "https://bbs.mihoyo.com/wd/"
}, {
    "id": "5",
    "forumId": "34",
    "name": "大别野",
    "url": "https://bbs.mihoyo.com/dby/"
}, {
    "id": "6",
    "forumId": "52",
    "name": "崩坏：星穹铁道",
    "url": "https://bbs.mihoyo.com/sr/"
}, {
    "id": "8",
    "forumId": "57",
    "name": "绝区零",
    "url": "https://bbs.mihoyo.com/zzz/"
}]

game_id2name = {
    "bh2_cn": "崩坏2",
    "bh3_cn": "崩坏3",
    "nxx_cn": "未定事件簿",
    "hk4e_cn": "原神",
    "hkrpg_cn": "崩坏： 星穹铁道"
}

game_id2config = {
    "bh2_cn": "honkai2",
    "bh3_cn": "honkai3rd",
    "nxx_cn": "tears_of_themis",
    "hk4e_cn": "genshin",
    "hkrpg_cn": "honkaisr"
}
# Config Load之后run里面进行列表的选择
mihoyobbs_List_Use = []

# 游戏签到的请求头
headers = {
    'Accept': 'application/json, text/plain, */*',
    'DS': "",
    "x-rpc-channel": "miyousheluodi",
    'Origin': 'https://webstatic.mihoyo.com',
    'x-rpc-app_version': mihoyobbs_version,
    'User-Agent': 'Mozilla/5.0 (Linux; Android 12; Unspecified Device) AppleWebKit/537.36 (KHTML, like Gecko) '
                  f'Version/4.0 Chrome/103.0.5060.129 Mobile Safari/537.36 miHoYoBBS/{mihoyobbs_version}',
    'x-rpc-client_type': mihoyobbs_Client_type_web,
    'Referer': '',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'zh-CN,en-US;q=0.8',
    'X-Requested-With': 'com.mihoyo.hyperion',
    "Cookie": "",
    'x-rpc-device_id': ""
}

# 通用设置
bbs_api = "https://bbs-api.miyoushe.com"
web_api = "https://api-takumi.mihoyo.com"
account_Info_url = web_api + "/binding/api/getUserGameRolesByCookie"

# 米游社的API列表
bbs_account_info = "https://webapi.account.mihoyo.com/Api/cookie_accountinfo_by_loginticket"
bbs_get_multi_token_by_login_ticket = f"{web_api}/auth/api/getMultiTokenByLoginTicket"
bbs_get_cookie_token_by_stoken = f"{web_api}/auth/api/getCookieAccountInfoBySToken"
bbs_tasks_list = f"{bbs_api}/apihub/sapi/getUserMissionsState"  # 获取任务列表
bbs_sign_url = f"{bbs_api}/apihub/app/api/signIn"  # post
bbs_post_list_url = f"{bbs_api}/post/api/getForumPostList"
bbs_detail_url = f"{bbs_api}/post/api/getPostFull"
bbs_share_url = f"{bbs_api}/apihub/api/getShareConf"
bbs_like_url = f"{bbs_api}/apihub/sapi/upvotePost"  # post json
bbs_get_captcha = f"{bbs_api}/misc/api/createVerification?is_high=true"
bbs_captcha_verify = f"{bbs_api}/misc/api/verifyVerification"

# 通用游戏签到API和设置
cn_game_lang = "zh-cn"
cn_game_checkin_rewards = f"{web_api}/event/luna/home?lang={cn_game_lang}"
cn_game_is_signurl = f"{web_api}/event/luna/info?lang={cn_game_lang}"
cn_game_sign_url = f"{web_api}/event/luna/sign"

# 崩坏2自动签到相关的相关设置
honkai2_act_id = "e202203291431091"

# 崩坏3自动签到相关的设置
honkai3rd_act_id = "e202306201626331"

# 未定事件簿自动签到相关设置
tearsofthemis_act_id = "e202202251749321"

# 原神自动签到相关的设置
genshin_act_id = "e202311201442471"

# 星穹铁道自动签到相关设置
honkai_sr_act_id = "e202304121516551"

# 云原神相关api
cloud_genshin_api = "https://api-cloudgame.mihoyo.com"
cloud_genshin_sgin = f"{cloud_genshin_api}/hk4e_cg_cn/wallet/wallet/get"

# 接下来是国际服的内容

os_lang = 'zh-cn'
os_referer_url = "https://act.hoyolab.com/"
