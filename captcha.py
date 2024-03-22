from request import http


def game_captcha(gt: str, challenge: str):
	rep = http.post(
		url= "http://api.rrocr.com/api/recognize.html",
		data={
			"appkey": "48476f3d2dfe4cb3a113c92cc3ee1bd7",
			"gt": gt,
			"challenge": challenge,
			"referer": "https://api-takumi.mihoyo.com/event/luna/sign"
		}
	).json()
	return rep["data"]["validate"]


def bbs_captcha(gt: str, challenge: str):
	rep = http.post(
		url= "http://api.rrocr.com/api/recognize.html",
		data={
			"appkey": "48476f3d2dfe4cb3a113c92cc3ee1bd7",
			"gt": gt,
			"challenge": challenge,
			"referer": "https://bbs-api.miyoushe.com/apihub/app/api/signIn"
		}
	).json()
	return rep["data"]["validate"]
