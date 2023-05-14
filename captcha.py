import config
from loghelper import log
from request import http

# 需要注册后使用公益打码
# https://www.rrocr.com/user/index.html
# https://www.rrocr.com/
token = '8401903b14ca4aa4a2ef0fef4ad20363'


def game_captcha(gt: str, challenge: str):
    validate = geetest(gt, challenge, 'https://passport-api.mihoyo.com/account/ma-cn-passport/app/loginByPassword')
    return validate  # 失败返回None 成功返回validate


def bbs_captcha(gt: str, challenge: str):
    validate = geetest(gt, challenge,
                       "https://webstatic.mihoyo.com/bbs/event/signin-ys/index.html?bbs_auth_required=true&act_id"
                       "=e202009291139501&utm_source=bbs&utm_medium=mys&utm_campaign=icon")
    return validate  # 失败返回None 成功返回validate


def geetest(gt: str, challenge: str, referer: str):
    response = http.post('http://api.rrocr.com/api/recognize.html', params={
        'appkey': token,
        'gt': gt,
        'challenge': challenge,
        'referer': referer
    })
    data = response.json()
    if data['status'] != 0:
        log.warning(data['msg'])  # 打码失败输出错误信息
        return None
    return data['data']['validate']  # 失败返回None 成功返回validate