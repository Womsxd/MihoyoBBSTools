import setting
from gamecheckin import GameCheckin


class Honkai2(GameCheckin):
    def __init__(self):
        super(Honkai2, self).__init__("bh2_cn", setting.honkai2_checkin_rewards)
        self.headers['Referer'] = 'https://webstatic.mihoyo.com/bbs/event/signin/bh2/index.html?bbs_auth_required' \
                                  f'=true&act_id={setting.honkai2_Act_id}&bbs_presentation_style=fullscreen' \
                                  '&utm_source=bbs&utm_medium=mys&utm_campaign=icon'
        self.act_id = setting.honkai2_Act_id
        self.sign_api = setting.honkai2_Sign_url
        self.is_sign_api = setting.honkai2_Is_signurl
        self.game_mid = "hokai2"
        self.game_name = "崩坏学园2"
