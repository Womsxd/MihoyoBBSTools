import setting
from gamecheckin import GameCheckin


class Honkai2(GameCheckin):
    def __init__(self) -> None:
        super(Honkai2, self).__init__("bh2_cn")
        self.headers['Referer'] = 'https://webstatic.mihoyo.com/bbs/event/signin/bh2/index.html?bbs_auth_required' \
                                  f'=true&act_id={setting.honkai2_act_id}&bbs_presentation_style=fullscreen' \
                                  '&utm_source=bbs&utm_medium=mys&utm_campaign=icon'
        self.act_id = setting.honkai2_act_id
        self.game_mid = "honkai2"
        self.game_name = "崩坏学园2"
        self.init()
