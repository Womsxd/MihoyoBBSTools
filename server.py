# Server Mod
import os
import time
import push
import config
import threading
import main as single
import main_multi as multi
from loghelper import log


class ServerConfig:
    """服务器配置类，提供线程安全的配置访问"""
    
    def __init__(self):
        """初始化配置"""
        self.time_interval = 720  # 默认签到间隔时间，单位分钟
        self.mod = 1  # 单用户模式/自动判断
        self.show_details = False  # 是否显示详细信息
        self.lock = threading.Lock()  # 线程锁
        
    def set_time_interval(self, interval):
        """
        设置时间间隔
        
        Args:
            interval (int): 时间间隔（分钟）
            
        Returns:
            bool: 设置是否成功
        """
        with self.lock:
            if isinstance(interval, int) and interval > 0:
                self.time_interval = interval
                return True
            return False
            
    def set_mod(self, mod):
        """
        设置模式
        
        Args:
            mod (int): 模式（1为单用户，2为多用户）
            
        Returns:
            bool: 设置是否成功
        """
        with self.lock:
            if mod in [1, 2]:
                self.mod = mod
                return True
            return False
            
    def set_show_details(self, show):
        """
        设置是否显示详细信息
        
        Args:
            show (bool): 是否显示详细信息
        """
        with self.lock:
            self.show_details = show
            
    def get_time_interval(self):
        """
        获取时间间隔
        
        Returns:
            int: 时间间隔（分钟）
        """
        with self.lock:
            return self.time_interval
            
    def get_mod(self):
        """
        获取模式
        
        Returns:
            int: 模式（1为单用户，2为多用户）
        """
        with self.lock:
            return self.mod
            
    def get_show_details(self):
        """
        获取是否显示详细信息
        
        Returns:
            bool: 是否显示详细信息
        """
        with self.lock:
            return self.show_details


class CommandHandler:
    """处理用户命令的类"""
    
    def __init__(self, config, detal_event, stop_event):
        """
        初始化命令处理器
        
        Args:
            config: 服务器配置对象
            detal_event: 详细信息显示事件
            stop_event: 停止服务器事件
        """
        self.config = config
        self.detal_event = detal_event
        self.stop_event = stop_event
        self.running = True
        
        # 命令帮助信息
        self.help_text = (
            "command windows\n"
            "stop: stop server\n"
            "reload: reload config and refresh time\n"
            "test: test current config\n"
            "single: test single config\n"
            "multi: test multi config\n"
            "mod x: x is refer single or multi, 1 is single, 2 is multi\n"
            "add 'yourcookie': add new user with cookie\n"
            "set user attribute value: such set username(*.yaml) enable(attribute) True(value)\n"
            "time x: set interval time (minute)\n"
            "show true/false: show the time count\n"
            "help: show this help message"
        )
        
    def handle_command(self, command_str):
        """
        处理用户输入的命令
        
        Args:
            command_str (str): 用户输入的命令字符串
            
        Returns:
            bool: 如果需要重新加载配置返回True，如果需要停止服务器返回False，否则返回None
        """
        if not command_str:
            log.info(self.help_text)
            return None
            
        # 解析命令
        command, args = self._parse_command(command_str)
        
        # 处理命令
        try:
            if command in ["help", "?"]:
                self._handle_help_command()
                return None
            elif command in ["stop", "exit"]:
                return self._handle_stop_command()
            elif command == "reload":
                return self._handle_reload_command()
            elif command == "test":
                self._handle_test_command()
                return None
            elif command == "single":
                self._handle_single_command()
                return None
            elif command == "multi":
                self._handle_multi_command()
                return None
            elif command == "time":
                return self._handle_time_command(args)
            elif command == "mod":
                self._handle_mod_command(args)
                return None
            elif command == "show":
                self._handle_show_command(args)
                return None
            elif command == "add":
                self._handle_add_command(args)
                return None
            elif command == "set":
                self._handle_set_command(args)
                return None
            else:
                log.info(f"Unknown command: {command}")
                log.info(self.help_text)
                return None
        except Exception as e:
            log.info(f"Error handling command '{command}': {e}")
            return None
        
    def _handle_help_command(self):
        """处理help命令"""
        log.info(self.help_text)
        
    def _handle_stop_command(self):
        """处理stop命令"""
        log.info("Stopping Server Please Wait")
        return False
        
    def _handle_reload_command(self):
        """处理reload命令"""
        log.info("Reloading configuration")
        return True
        
    def _handle_test_command(self):
        """处理test命令"""
        log.info("Testing current configuration")
        if self.config.get_mod() == 1:
            try:
                single.main()
            except Exception as e:
                log.info(f"single_user start failed: {e}")
        else:
            try:
                multi.main_multi(True)
            except Exception as e:
                log.info(f"multi_user start failed: {e}")
                
    def _handle_single_command(self):
        """处理single命令"""
        log.info("Testing single user configuration")
        try:
            single.main()
        except Exception as e:
            log.info(f"single_user start failed: {e}")
            
    def _handle_multi_command(self):
        """处理multi命令"""
        log.info("Testing multi user configuration")
        try:
            multi.main_multi(True)
        except Exception as e:
            log.info(f"multi_user start failed: {e}")
            
    def _handle_time_command(self, args):
        """处理time命令"""
        if not self._validate_args("time", args, 1):
            return None
            
        try:
            interval = int(args[0])
            if self.config.set_time_interval(interval):
                log.info(f"Switching interval to {interval} minute(s)")
                return True  # 需要重新加载配置
            else:
                log.info("Invalid time interval. Must be a positive integer.")
                return None
        except ValueError:
            log.info("Invalid time interval. Must be a number.")
            return None
            
    def _handle_mod_command(self, args):
        """处理mod命令"""
        if not self._validate_args("mod", args, 1):
            return
            
        try:
            mod = int(args[0])
            if self.config.set_mod(mod):
                log.info(f"Switching mod to {mod}")
            else:
                log.info("Invalid mod. Must be 1 (single) or 2 (multi).")
        except ValueError:
            log.info("Invalid mod. Must be a number.")
            
    def _handle_show_command(self, args):
        """处理show命令"""
        if not self._validate_args("show", args, 1):
            return
            
        if args[0].lower() == "true":
            self.config.set_show_details(True)
            self.detal_event.set()
            log.info("Switching to detail mode")
        elif args[0].lower() == "false":
            self.config.set_show_details(False)
            self.detal_event.clear()
            log.info("Switching to silent mode")
        else:
            log.info("Invalid value for show command. Use 'true' or 'false'.")
            
    def _handle_add_command(self, args):
        """处理add命令"""
        if not args:
            log.info("Please provide a cookie to add.")
            return
            
        # 合并所有参数作为cookie（因为cookie可能包含空格）
        cookie = " ".join(args)
        log.info("Adding new user")
        
        if self.config.get_mod() == 1:
            name = "config"
        else:
            log.info("Please input your config name (*.yaml):")
            name = input().strip()
            
        try:
            new_config = config.copy_config()
            new_config['account']['cookie'] = cookie
            file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "config", f"{name}.yaml")
            config.save_config(file_path, new_config)
            log.info("Saving OK")
        except Exception as e:
            log.info(f'Saving failed, please check your file system: {e}')
            
    def _handle_set_command(self, args):
        """处理set命令"""
        if not self._validate_args("set", args, 3):
            return
            
        username, attribute, value = args
        file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "config", f"{username}.yaml")
        
        if not os.path.exists(file_path):
            log.info("User does not exist")
            return
            
        try:
            new_config = config.load_config(file_path)
            
            # 转换值类型
            if value.lower() == "true":
                value = True
            elif value.lower() == "false":
                value = False
            elif value.isdigit():
                value = int(value)
                
            new_config[attribute] = value
            config.save_config(file_path, new_config)
            log.info("Saving OK")
        except Exception as e:
            log.info(f'Saving failed, please check your file system: {e}')
        
    def _parse_command(self, command_str):
        """
        解析命令字符串
        
        Args:
            command_str (str): 命令字符串
            
        Returns:
            tuple: (command, args) 命令和参数列表
        """
        parts = command_str.strip().split()
        if not parts:
            return "", []
            
        command = parts[0].lower()
        args = parts[1:] if len(parts) > 1 else []
        
        return command, args
        
    def _validate_args(self, command, args, expected_count):
        """
        验证命令参数数量
        
        Args:
            command (str): 命令名称
            args (list): 参数列表
            expected_count (int): 期望的参数数量
            
        Returns:
            bool: 参数数量是否正确
        """
        if len(args) != expected_count:
            log.info(f"Invalid number of arguments for command '{command}'. Expected {expected_count}, got {len(args)}.")
            return False
        return True


def runningtime():
    """获取当前时间戳"""
    return int(time.time())


def control(config, stop_event):
    """
    控制函数，定期执行任务
    
    Args:
        config: 服务器配置对象
        stop_event: 停止事件
    """
    last_time = runningtime()
    while True:
        now_time = runningtime()
        if now_time > last_time + config.get_time_interval() * 60:
            last_time = runningtime()
            if config.get_mod() == 1:
                try:
                    single.task_run()
                except Exception as e:
                    log.info(f"single_user start failed: {e}")
            else:
                try:
                    status, push_message = multi.main_multi(True)
                    push.push(status, push_message)
                except Exception as e:
                    log.info(f"multi_user start failed: {e}")
        if stop_event.is_set():
            log.info("Stopping threading")
            break
        if config.get_show_details():
            log.info("The Next check time is {}s".format(
                last_time + config.get_time_interval() * 60 - now_time))
        time.sleep(20)


def command_loop(config):
    """
    命令循环函数
    
    Args:
        config: 服务器配置对象
    """
    detal = threading.Event()
    t1_stop = threading.Event()
    thread1 = threading.Thread(
        name='time_check',
        target=control,
        args=(config, t1_stop)
    )
    thread1.start()
    
    command_handler = CommandHandler(config, detal, t1_stop)
    
    try:
        while True:
            command_str = input()
            result = command_handler.handle_command(command_str)
            
            if result is False:  # 停止服务器
                t1_stop.set()
                break
            elif result is True:  # 重新加载配置
                t1_stop.set()
                thread1.join()
                t1_stop = threading.Event()
                thread1 = threading.Thread(
                    name='time_check',
                    target=control,
                    args=(config, t1_stop)
                )
                thread1.start()
    except Exception as e:
        log.info(f"Command loop error: {e}")
        t1_stop.set()
    finally:
        thread1.join()


if __name__ == '__main__':
    log.info('Running in Server Mode')
    
    # 初始化配置
    config = ServerConfig()
    
    # 检查配置文件存在以确定模式
    config_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "config", "config.yaml")
    if os.path.exists(config_path):
        config.set_mod(1)
    else:
        config.set_mod(2)
    
    log.info(f"Switching to mode {config.get_mod()}")
    
    # 启动命令循环
    command_loop(config)
