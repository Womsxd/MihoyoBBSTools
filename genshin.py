import setting
from gamecheckin import GameCheckin


class Genshin(GameCheckin):
    def __init__(self) -> None:
        super(Genshin, self).__init__("hk4e_cn")
        self.headers['Referer'] = f'https://act.mihoyo.comb'
        self.act_id = setting.genshin_act_id
        self.game_mid = "genshin"
        self.game_name = "原神"
        self.player_name = "旅行者"
        self.init()
