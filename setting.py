# 米游社的Salt
# java提取，会跟随版本更新
mihoyobbs_salt = "oqrJbPCoFhWhFBNDvVRuldbrbiVxyWsP"
mihoyobbs_salt_web = "zZDfHqEcwTqvvKDmqRcHyqqurxGgLfBV"
# so提取 一般不会变
mihoyobbs_salt_x4 = "xV8v4Qu54lUKrEYFZkJhB8cuOh9Asafs"
mihoyobbs_salt_x6 = "t0qEgfub6cvueAPgR5m9aQWWVciEer7v"
# 部分接口要带
mihoyobbs_verify_key = "bll8iq97cem8"
# 米游社的版本
mihoyobbs_version = "2.75.2"  # Salt和Version相互对应
# 米游社的客户端类型
mihoyobbs_Client_type = "2"  # 1为ios 2为安卓
mihoyobbs_Client_type_web = "5"  # 4为pc web 5为mobile web

# 米游社的分区列表
mihoyobbs_List = {
    1: {"id": "1", "forumId": "1", "name": "崩坏3"},
    2: {"id": "2", "forumId": "26", "name": "原神"},
    3: {"id": "3", "forumId": "30", "name": "崩坏2"},
    4: {"id": "4", "forumId": "37", "name": "未定事件簿"},
    5: {"id": "5", "forumId": "34", "name": "大别野"},
    6: {"id": "6", "forumId": "52", "name": "崩坏：星穹铁道"},
    8: {"id": "8", "forumId": "57", "name": "绝区零"}
}

game_id2name = {
    "bh2_cn": "崩坏2",
    "bh3_cn": "崩坏3",
    "nxx_cn": "未定事件簿",
    "hk4e_cn": "原神",
    "hkrpg_cn": "崩坏： 星穹铁道",
    "nap_cn": "绝区零"
}

game_id2config = {
    "bh2_cn": "honkai2",
    "bh3_cn": "honkai3rd",
    "nxx_cn": "tears_of_themis",
    "hk4e_cn": "genshin",
    "hkrpg_cn": "honkaisr",
    "nap_cn": "zzz"
}

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
passport_api = "https://passport-api.mihoyo.com"

account_Info_url = web_api + "/binding/api/getUserGameRolesByCookie"
get_token_by_stoken = f"{passport_api}/account/ma-cn-session/app/getTokenBySToken"

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

hk4e_api_base_url = 'https://hk4e-api.mihoyo.com'
# 获取hk4e token对应的账号信息
hk4e_token_get_info_url = f'{web_api}/common/badge/v1/login/info'
# 获取hk4e token
get_hk4e_token_url = f'{web_api}/common/badge/v1/login/account'
genius_invokation_status = f'{hk4e_api_base_url}/event/geniusinvokationtcg/rd_info'
# 获取任务列表
genius_invokation_task_url = f'{hk4e_api_base_url}/event/geniusinvokationtcg/adventure_task_list'
# 领取任务奖励
genius_invokation_get_award_url = f'{hk4e_api_base_url}/event/geniusinvokationtcg/award_adventure_task'
# 提交任务完成
genius_invokation_finish_task_url = f'{hk4e_api_base_url}/event/geniusinvokationtcg/finish_adventure_task'

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

# 绝区零自动签到相关设置
zzz_web_api = 'https://act-nap-api.mihoyo.com'
zzz_game_checkin_rewards = f"{zzz_web_api}/event/luna/zzz/home?lang={cn_game_lang}"
zzz_game_is_signurl = f"{zzz_web_api}/event/luna/zzz/info?lang={cn_game_lang}"
zzz_game_sign_url = f"{zzz_web_api}/event/luna/zzz/sign"
zzz_act_id = "e202406242138391"

# 云原神相关api
cloud_genshin_api = "https://api-cloudgame.mihoyo.com"
cloud_genshin_sgin = f"{cloud_genshin_api}/hk4e_cg_cn/wallet/wallet/get"

# 接下来是国际服的内容
os_referer_url = "https://act.hoyolab.com/"
os_genshin_act_id = "e202102251931481"
os_honkai_sr_act_id = "e202303301540311"
os_honkai3rd_act_id = "e202110291205111"
os_tearsofthemis_act_id = "e202202281857121"
os_zzz_act_id = "e202406031448091"
