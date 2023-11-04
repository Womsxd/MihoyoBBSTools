import config
from hoyo_checkin import hoyo_checkin


def run():
    cookie_str = config.config.get("games", {}).get(
        "os",  {}).get("cookie", "")
    ret_msg = '原神:\n' + hoyo_checkin("https://sg-hk4e-api.hoyolab.com/event/sol",
                                     "e202102251931481", cookie_str)
    return ret_msg
