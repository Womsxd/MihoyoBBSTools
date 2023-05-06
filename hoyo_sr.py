import config
from hoyo_checkin import hoyo_checkin


def run():
    cookie_str = config.config.get("games", {}).get(
        "os",  {}).get("cookie", "")
    hoyo_checkin("https://sg-public-api.hoyolab.com/event/luna/os",
                 "e202303301540311",
                 cookie_str,)
