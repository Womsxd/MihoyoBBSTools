import setting
from gamecheckin import GameCheckin


class Genshin(GameCheckin):
    def __init__(self) -> None:
        super(Genshin, self).__init__("hk4e_cn", setting.genshin_checkin_rewards)
        self.headers['Referer'] = f'https://webstatic.mihoyo.com/bbs/event/signin-ys/index.html?bbs_auth_required=tru' \
                                  f'e&act_id={setting.genshin_act_id}&utm_source=bbs&utm_medium=mys&utm_campaign=icon'
        self.act_id = setting.genshin_act_id
        self.sign_api = setting.genshin_signurl
        self.is_sign_api = setting.genshin_is_signurl
        self.game_mid = "genshin"
        self.game_name = "原神"
        self.player_name = "旅行者"
