from request import http


def game_captcha(gt: str, challenge: str):
	appkey=config.config['captcha']['token']
	log.warning(f"appkeygame：{appkey}")
	rep = http.post(
		url= "http://api.rrocr.com/api/recognize.html",
		data={
			"appkey": appkey,
			"gt": gt,
			"challenge": challenge,
			"referer": "https://api-takumi.mihoyo.com/event/luna/sign"
		}
	).json()
	return rep["data"]["validate"]


def bbs_captcha(gt: str, challenge: str):
	appkey=config.config['captcha']['token']
	log.warning(f"appkeybbs：{appkey}")
	rep = http.post(
		url= "http://api.rrocr.com/api/recognize.html",
		data={
			"appkey": appkey,
			"gt": gt,
			"challenge": challenge,
			"referer": "https://bbs-api.miyoushe.com/apihub/app/api/signIn"
		}
	).json()
	return rep["data"]["validate"]
