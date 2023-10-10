import setting
from gamecheckin import GameCheckin


class Tears_of_themis(GameCheckin):
    def __init__(self) -> None:
        super(Tears_of_themis, self).__init__("nxx_cn")
        self.headers['Referer'] = 'https://webstatic.mihoyo.com/bbs/event/signin/nxx/index.html?bbs_auth_required' \
                                  '=true&bbs_presentation_style=fullscreen' \
                                  f'act_id={setting.tearsofthemis_act_id}'
        self.act_id = setting.tearsofthemis_act_id
        self.game_mid = "tears_of_themis"
        self.game_name = "未定事件簿"
        self.player_name = "律师"
        self.init()
        