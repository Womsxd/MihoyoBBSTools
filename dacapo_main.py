import os
import sys
import json
import yaml
import tempfile
from pathlib import Path
from typing import Dict, Any, List
from configparser import ConfigParser


def setup_logging():
    config_dir = Path(__file__).parent / "config"
    logging_ini = config_dir / "logging.ini"
    logging_example = config_dir / "logging.ini.example"
    
    if not logging_ini.exists() and logging_example.exists():
        config_parser = ConfigParser(interpolation=None)
        config_parser.read(logging_example, encoding='utf-8')
        
        if config_parser.has_section('formatter_simpleFormatter'):
            config_parser.set('formatter_simpleFormatter', 'format', '%(asctime)s - %(levelname)s - %(message)s')
            config_parser.set('formatter_simpleFormatter', 'datefmt', '%Y-%m-%d %H:%M:%S')
        
        with open(logging_ini, 'w', encoding='utf-8') as f:
            config_parser.write(f)
        
        print(f"已创建日志配置文件: {logging_ini}")
    
    elif not logging_ini.exists():
        print("未找到 logging.ini.example，将使用默认日志配置")


setup_logging()

import config
import main
from loghelper import log


class DaCapoAdapter:
    """DaCapo 适配器，负责将 DaCapo 配置转换为原生配置并执行任务"""
    
    def __init__(self, config_path: str):
        self.config_path = config_path
        self.dacapo_config = self._load_dacapo_config()
        
    def _load_dacapo_config(self) -> Dict[str, Any]:
        """加载 DaCapo 配置文件"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            log.error(f"加载 DaCapo 配置文件失败: {e}")
            sys.exit(1)
    
    def _convert_text_to_list(self, text: str) -> List[str]:
        """转换文本为字符串列表"""
        return [item.strip() for item in (text or "").split(',') if item.strip()]
    
    def _convert_black_list(self, text: str) -> List[str]:
        """转换黑名单文本为列表"""
        return self._convert_text_to_list(text)
    
    def _convert_checkin_list(self, text: str) -> List[int]:
        """转换签到列表文本为整数列表"""
        if not text or not text.strip():
            return [5, 2]
        try:
            return [int(item.strip()) for item in text.split(',') if item.strip()]
        except ValueError:
            log.warning("签到列表格式错误，使用默认值")
            return [5, 2]
    
    def _convert_activities_list(self, text: str) -> List[str]:
        """转换活动列表文本为列表"""
        return self._convert_text_to_list(text)
    
    def validate_config(self) -> tuple:
        """验证配置的有效性"""
        project_config = self.dacapo_config.get("Project", {}).get("General", {})
        task_config = self.dacapo_config.get("日常", {}).get("米游社", {})
        
        cookie = project_config.get("账号配置", {}).get("米游社Cookie", "").strip()
        if not cookie:
            return False, "米游社Cookie不能为空"
        
        checkin_list = task_config.get("米游社BBS", {}).get("签到版块列表", "")
        try:
            self._convert_checkin_list(checkin_list)
        except:
            return False, "签到版块列表格式错误，应为用逗号分隔的数字"
        
        retries = task_config.get("国服游戏", {}).get("重试次数", "3")
        try:
            int(retries)
        except ValueError:
            return False, "重试次数必须是数字"
        
        return True, "配置验证通过"
    
    def convert_to_native_config(self) -> Dict[str, Any]:
        """将 DaCapo 配置转换为项目原生配置"""
        project_config = self.dacapo_config.get("Project", {}).get("General", {})
        task_config = self.dacapo_config.get("日常", {}).get("米游社", {})
        
        native_config = {
            "enable": True,
            "version": 15,
            "push": ""
        }
        
        account_group = project_config.get("账号配置", {})
        native_config["account"] = {
            "cookie": account_group.get("米游社Cookie", ""),
            "stuid": account_group.get("stuid", ""),
            "stoken": account_group.get("stoken", ""),
            "mid": account_group.get("mid", "")
        }
        
        device_group = project_config.get("设备信息", {})
        native_config["device"] = {
            "name": device_group.get("设备名称", "Xiaomi MI 6"),
            "model": device_group.get("设备型号", "Mi 6"),
            "id": device_group.get("设备ID", ""),
            "fp": device_group.get("设备指纹", "")
        }
        
        bbs_group = task_config.get("米游社BBS", {})
        checkin_list_text = bbs_group.get("签到版块列表", "5,2")
        native_config["mihoyobbs"] = {
            "enable": bbs_group.get("启用米游社签到", True),
            "checkin": bbs_group.get("启用版块签到", True),
            "checkin_list": self._convert_checkin_list(checkin_list_text),
            "read": bbs_group.get("启用看帖", True),
            "like": bbs_group.get("启用点赞", True),
            "cancel_like": bbs_group.get("启用取消点赞", True),
            "share": bbs_group.get("启用分享", True)
        }
        
        cn_games_group = task_config.get("国服游戏", {})
        native_config["games"] = {
            "cn": {
                "enable": cn_games_group.get("启用国服签到", True),
                "useragent": cn_games_group.get("User Agent", 
                    "Mozilla/5.0 (Linux; Android 12; Unspecified Device) AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Version/4.0 Chrome/103.0.5060.129 Mobile Safari/537.36"),
                "retries": int(cn_games_group.get("重试次数", 3)),
                "genshin": {
                    "checkin": cn_games_group.get("原神签到", True),
                    "black_list": self._convert_black_list(cn_games_group.get("原神黑名单", ""))
                },
                "honkai2": {
                    "checkin": cn_games_group.get("崩坏2签到", False),
                    "black_list": self._convert_black_list(cn_games_group.get("崩坏2黑名单", ""))
                },
                "honkai3rd": {
                    "checkin": cn_games_group.get("崩坏3签到", False),
                    "black_list": self._convert_black_list(cn_games_group.get("崩坏3黑名单", ""))
                },
                "tears_of_themis": {
                    "checkin": cn_games_group.get("未定事件簿签到", False),
                    "black_list": self._convert_black_list(cn_games_group.get("未定事件簿黑名单", ""))
                },
                "honkai_sr": {
                    "checkin": cn_games_group.get("星穹铁道签到", False),
                    "black_list": self._convert_black_list(cn_games_group.get("星穹铁道黑名单", ""))
                },
                "zzz": {
                    "checkin": cn_games_group.get("绝区零签到", False),
                    "black_list": self._convert_black_list(cn_games_group.get("绝区零黑名单", ""))
                }
            },
            "os": {
                "enable": False,
                "cookie": "",
                "lang": "zh-cn",
                "genshin": {"checkin": False, "black_list": []},
                "honkai3rd": {"checkin": False, "black_list": []},
                "tears_of_themis": {"checkin": False, "black_list": []},
                "honkai_sr": {"checkin": False, "black_list": []},
                "zzz": {"checkin": False, "black_list": []}
            }
        }
        
        os_games_group = task_config.get("国际服游戏", {})
        if os_games_group.get("启用国际服签到", False):
            native_config["games"]["os"] = {
                "enable": True,
                "cookie": os_games_group.get("国际服Cookie", ""),
                "lang": os_games_group.get("语言设置", "zh-cn"),
                "genshin": {
                    "checkin": os_games_group.get("国际服原神签到", False),
                    "black_list": self._convert_black_list(os_games_group.get("国际服原神黑名单", ""))
                },
                "honkai3rd": {
                    "checkin": os_games_group.get("国际服崩坏3签到", False),
                    "black_list": self._convert_black_list(os_games_group.get("国际服崩坏3黑名单", ""))
                },
                "tears_of_themis": {
                    "checkin": os_games_group.get("国际服未定事件簿签到", False),
                    "black_list": self._convert_black_list(os_games_group.get("国际服未定事件簿黑名单", ""))
                },
                "honkai_sr": {
                    "checkin": os_games_group.get("国际服星穹铁道签到", False),
                    "black_list": self._convert_black_list(os_games_group.get("国际服星穹铁道黑名单", ""))
                },
                "zzz": {
                    "checkin": os_games_group.get("国际服绝区零签到", False),
                    "black_list": self._convert_black_list(os_games_group.get("国际服绝区零黑名单", ""))
                }
            }
        
        cloud_games_group = task_config.get("云游戏", {})
        native_config["cloud_games"] = {
            "cn": {
                "enable": cloud_games_group.get("启用云游戏签到", False),
                "genshin": {
                    "enable": cloud_games_group.get("启用云原神", False),
                    "token": cloud_games_group.get("云原神Token", "")
                },
                "zzz": {
                    "enable": cloud_games_group.get("启用云绝区零", False),
                    "token": cloud_games_group.get("云绝区零Token", "")
                }
            },
            "os": {
                "enable": cloud_games_group.get("启用国际服云游戏", False),
                "lang": cloud_games_group.get("国际服云游戏语言", "zh-cn"),
                "genshin": {
                    "enable": cloud_games_group.get("启用国际服云原神", False),
                    "token": cloud_games_group.get("国际服云原神Token", "")
                }
            }
        }
        
        native_config["competition"] = {
            "enable": False,
            "genius_invokation": {
                "enable": False,
                "account": [],
                "checkin": False,
                "weekly": False
            }
        }
        
        web_activity_group = task_config.get("网页活动", {})
        activities_text = web_activity_group.get("活动列表", "")
        native_config["web_activity"] = {
            "enable": web_activity_group.get("启用网页活动", False),
            "activities": self._convert_activities_list(activities_text)
        }
        
        return native_config
    
    def create_push_config(self, project_config: Dict[str, Any]) -> str:
        """创建推送配置文件"""
        push_group = project_config.get("推送设置", {})
        
        if not push_group.get("启用推送", False):
            return None
            
        try:
            temp_fd, temp_path = tempfile.mkstemp(suffix='.ini', prefix='dacapo_push_')
            os.close(temp_fd)
            
            push_config = ConfigParser()
            
            push_service = push_group.get("推送服务", "pushplus")
            push_token = push_group.get("推送Token", "")
            error_only = push_group.get("仅错误时推送", False)
            topic = push_group.get("推送群组", "")
            block_keys = push_group.get("屏蔽关键词", "")
            
            push_config.add_section('setting')
            push_config.set('setting', 'enable', 'true')
            push_config.set('setting', 'push_server', push_service)
            push_config.set('setting', 'push_token', push_token)
            push_config.set('setting', 'push_block_keys', block_keys)
            push_config.set('setting', 'error_push_only', str(error_only).lower())
            if topic:
                push_config.set('setting', 'topic', topic)
            
            service_configs = {
                "telegram": {
                    "section": "telegram",
                    "config": {
                        "api_url": "api.telegram.org",
                        "bot_token": push_token,
                        "chat_id": ""
                    }
                },
                "wecom": {
                    "section": "wecom",
                    "config": {
                        "wechat_id": "",
                        "agentid": "",
                        "secret": push_token,
                        "touser": "@all"
                    }
                },
                "dingrobot": {
                    "section": "dingrobot", 
                    "config": {
                        "webhook": push_token,
                        "secret": ""
                    }
                },
                "feishubot": {
                    "section": "feishubot",
                    "config": {
                        "webhook": push_token
                    }
                },
                "bark": {
                    "section": "bark",
                    "config": {
                        "api_url": "https://api.day.app",
                        "token": push_token,
                        "icon": "genshin"
                    }
                },
                "pushdeer": {
                    "section": "pushdeer",
                    "config": {
                        "api_url": "https://api2.pushdeer.com",
                        "token": push_token
                    }
                },
                "gotify": {
                    "section": "gotify",
                    "config": {
                        "api_url": "",
                        "token": push_token,
                        "priority": "5"
                    }
                },
                "smtp": {
                    "section": "smtp",
                    "config": {
                        "mailhost": "",
                        "port": "587",
                        "fromaddr": "",
                        "toaddr": "",
                        "username": "",
                        "password": push_token,
                        "subject": "米游社签到脚本",
                        "ssl_enable": "true",
                        "background": "true"
                    }
                },
                "webhook": {
                    "section": "webhook",
                    "config": {
                        "webhook_url": push_token
                    }
                },
                "qmsg": {
                    "section": "qmsg",
                    "config": {
                        "key": push_token
                    }
                },
                "discord": {
                    "section": "discord",
                    "config": {
                        "webhook": push_token
                    }
                },
                "wxpusher": {
                    "section": "wxpusher",
                    "config": {
                        "app_token": push_token,
                        "uids": "",
                        "topic_ids": topic
                    }
                },
                "serverchan3": {
                    "section": "serverchan3",
                    "config": {
                        "sendkey": push_token,
                        "tags": ""
                    }
                },
                "pushme": {
                    "section": "pushme",
                    "config": {
                        "token": push_token,
                        "url": "https://push.i-i.me/"
                    }
                },
                "cqhttp": {
                    "section": "cqhttp",
                    "config": {
                        "cqhttp_url": "http://127.0.0.1:5000/send_msg",
                        "cqhttp_qq": "10001",
                        "cqhttp_group": "10002"
                    }
                }
            }
            
            if push_service in service_configs:
                service_conf = service_configs[push_service]
                push_config.add_section(service_conf["section"])
                for key, value in service_conf["config"].items():
                    if value:
                        push_config.set(service_conf["section"], key, str(value))
            
            with open(temp_path, 'w', encoding='utf-8') as f:
                push_config.write(f)
            
            return temp_path
            
        except Exception as e:
            log.error(f"创建推送配置文件失败: {e}")
            return None
    
    def create_temp_config(self, native_config: Dict[str, Any]) -> str:
        """创建临时配置文件"""
        try:
            temp_fd, temp_path = tempfile.mkstemp(suffix='.yaml', prefix='dacapo_config_')
            
            with os.fdopen(temp_fd, 'w', encoding='utf-8') as f:
                yaml.dump(native_config, f, default_flow_style=False, 
                         allow_unicode=True, sort_keys=False)
            
            return temp_path
        except Exception as e:
            log.error(f"创建临时配置文件失败: {e}")
            sys.exit(1)
    
    def run_task(self):
        """执行任务"""
        temp_push_path = None
        temp_config_path = None
        try:
            log.info("开始执行 DaCapo 适配任务")
            log.info("验证配置...")
            is_valid, validation_msg = self.validate_config()
            if not is_valid:
                log.error(f"配置验证失败: {validation_msg}")
                return 1

            log.info("转换配置...")
            native_config = self.convert_to_native_config()
            project_config = self.dacapo_config.get("Project", {}).get("General", {})
            temp_push_path = self.create_push_config(project_config)
            if temp_push_path:
                log.info("推送配置已创建")
                os.environ["AutoMihoyoBBS_push_path"] = os.path.dirname(temp_push_path)
                os.environ["AutoMihoyoBBS_push_name"] = os.path.basename(temp_push_path)

            log.info("创建临时配置文件...")
            temp_config_path = self.create_temp_config(native_config)
            config.config_Path = temp_config_path

            log.info("执行米游社签到任务...")
            status_code, message = main.main()

            if temp_push_path:
                log.info("推送执行结果...")
                import push
                push.push(status_code, message)

            log.info("=" * 50)
            log.info("任务执行完成!")
            log.info(f"状态码: {status_code}")
            log.info("执行结果:")
            for line in message.split('\n'):
                if line.strip():
                    log.info(line)
            log.info("=" * 50)
            return status_code

        except Exception as e:
            log.error(f"执行任务失败: {e}")
            import traceback
            log.error("异常详情:")
            for line in traceback.format_exc().split('\n'):
                if line.strip():
                    log.error(line)
            return 1
        finally:
            # 清理临时配置文件
            if temp_config_path and os.path.exists(temp_config_path):
                try:
                    os.unlink(temp_config_path)
                    log.debug("临时配置文件已清理")
                except Exception as cleanup_error:
                    log.warning(f"清理临时文件失败: {cleanup_error}")
            # 清理推送配置文件和环境变量
            if temp_push_path and os.path.exists(temp_push_path):
                try:
                    os.unlink(temp_push_path)
                except Exception as cleanup_error:
                    log.warning(f"清理推送配置文件失败: {cleanup_error}")
            for env_key in ("AutoMihoyoBBS_push_path", "AutoMihoyoBBS_push_name"):
                if env_key in os.environ:
                    del os.environ[env_key]


def run():
    """主函数"""
    if len(sys.argv) < 2:
        log.error("用法: python dacapo_main.py <配置文件路径>")
        sys.exit(1)
    
    config_path = sys.argv[1]
    
    if not os.path.exists(config_path):
        log.error(f"配置文件不存在: {config_path}")
        sys.exit(1)
    
    adapter = DaCapoAdapter(config_path)
    adapter.run_task()


if __name__ == "__main__":
    run()
