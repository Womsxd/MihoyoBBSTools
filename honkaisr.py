import setting
from gamecheckin import GameCheckin


class Honkaisr(GameCheckin):
    def __init__(self):
        super(Honkaisr, self).__init__("hkrpg_cn")
        self.headers['Referer'] = 'https://act.mihoyo.com/'
        self.headers["Origin"] = "https://act.mihoyo.com"
        self.act_id = setting.honkai_sr_act_id
        self.game_mid = "honkai_sr"
        self.game_name = "崩坏: 星穹铁道"
        self.player_name = "开拓者"
        self.init()
