from request import http
from twocaptcha import TwoCaptcha
import json
import config


def game_captcha(gt: str, challenge: str):
    validate = geetest(gt, challenge, 'https://passport-api.mihoyo.com/account/ma-cn-passport/app/loginByPassword')
    return validate  # 失败返回None 成功返回validate


def bbs_captcha(gt: str, challenge: str):
    validate = geetest(gt, challenge,
                       "https://webstatic.mihoyo.com/bbs/event/signin-ys/index.html?bbs_auth_required=true&act_id"
                       "=e202009291139501&utm_source=bbs&utm_medium=mys&utm_campaign=icon")
    return validate  # 失败返回None 成功返回validate


def geetest(gt: str, challenge: str, referer: str):
    if config.config["captcha"]["api_key"]:
        api_key = config.config["captcha"]["api_key"]
        solver = TwoCaptcha(api_key)
        result = solver.geetest(gt=gt, challenge=challenge, url=referer)

        if result:
            result_code = result["code"]
            if result_code:
                json_result_code = json.loads(result_code)
                if json_result_code:
                    geetest_validate = json_result_code["geetest_validate"]
                    return geetest_validate

    return None
