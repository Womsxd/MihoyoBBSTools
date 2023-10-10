import setting
from gamecheckin import GameCheckin


class Honkai3rd(GameCheckin):
    def __init__(self) -> None:
        super(Honkai3rd, self).__init__("bh3_cn")
        self.headers['Referer'] = 'https://webstatic.mihoyo.com/bbs/event/signin/bh3/index.html?bbs_auth_required' \
                                  f'=true&act_id={setting.honkai3rd_act_id}&bbs_presentation_style=fullscreen' \
                                  '&utm_source=bbs&utm_medium=mys&utm_campaign=icon'
        self.act_id = setting.honkai3rd_act_id
        self.game_mid = "honkai3rd"
        self.game_name = "崩坏3"
        self.player_name = "舰长"
        self.init()
