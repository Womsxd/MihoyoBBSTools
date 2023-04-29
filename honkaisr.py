import setting
from gamecheckin import GameCheckin


class Honkaisr(GameCheckin):
    def __init__(self):
        super(Honkaisr, self).__init__("hkrpg_cn", setting.any_checkin_rewards.format(setting.honkai_sr_Act_id))
        self.headers['Referer'] = f'https://webstatic.mihoyo.com/bbs/event/signin/hkrpg/index.html?' \
                                  f'act_id={setting.honkai_sr_Act_id}&bbs_auth_required=true&bbs_presentation_style' \
                                  f'=fullscreen&utm_source=share&utm_medium=bbs&utm_campaign=app'
        self.act_id = setting.honkai_sr_Act_id
        self.game_mid = "honkai_sr"
        self.game_name = "崩坏: 星穹铁道"
        self.player_name = "开拓者"
