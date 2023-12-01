import setting
from gamecheckin import GameCheckin


class Genshin(GameCheckin):
    def __init__(self) -> None:
        super(Genshin, self).__init__("hk4e_cn")
        self.headers['Referer'] = 'https://act.mihoyo.com/'
        self.headers["Origin"] = "https://act.mihoyo.com"
        self.headers["x-rpc-signgame"] = "hk4e"
        self.act_id = setting.genshin_act_id
        self.game_mid = "genshin"
        self.game_name = "原神"
        self.player_name = "旅行者"
        self.init()
