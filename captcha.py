# from request import http

try:
    from mhylogin.shangcaptcha import bbs_captcha2, game_captcha2

    # 如果导入成功，你可以在这里使用导入的模块
    def game_captcha(gt: str, challenge: str):
        return game_captcha2(gt, challenge)

    def bbs_captcha(gt: str, challenge: str):
        return bbs_captcha2(gt, challenge)

except ImportError:
    # 如果导入失败，你可以在这里处理错误或执行其他操作
    def game_captcha(gt: str, challenge: str):
        return None  # 失败返回None 成功返回validate


    def bbs_captcha(gt: str, challenge: str):
        return None

__all__ = ["game_captcha", "bbs_captcha"]

