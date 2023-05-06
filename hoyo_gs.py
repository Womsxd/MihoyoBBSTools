import config
from hoyo_checkin import hoyo_checkin


def run():
    cookie_str = config.config.get("games", {}).get(
        "os",  {}).get("cookie", "")
    hoyo_checkin("https://hk4e-api-os.mihoyo.com/event/sol",
                 "e202102251931481",
                 cookie_str,)
