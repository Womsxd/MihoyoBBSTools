import argparse
import base64
import getpass
import hashlib
import json
import os
import socket
import ssl
import struct
import sys
import time
import urllib.parse
from configparser import ConfigParser

from request import get_new_session

API_BASE = "https://api.bot.qq.com"
C2C_INTENT = 1 << 25
WS_GUID = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"


class WebSocketError(Exception):
    def __init__(self, message, code=None):
        super().__init__(message)
        self.code = code


class WebSocketClient:
    """QQ 机器人网关所需的最小 WebSocket 客户端，避免引入额外依赖"""

    def __init__(self, url, timeout=30):
        parsed = urllib.parse.urlparse(url)
        if parsed.scheme != "wss":
            raise WebSocketError(f"不支持的 WebSocket 地址：{url}")
        host = parsed.hostname
        port = parsed.port or 443
        path = parsed.path or "/"
        if parsed.query:
            path = f"{path}?{parsed.query}"

        raw_sock = socket.create_connection((host, port), timeout=timeout)
        self.sock = ssl.create_default_context().wrap_socket(raw_sock, server_hostname=host)
        self.buffer = b""

        sec_key = base64.b64encode(os.urandom(16)).decode()
        handshake = (
            f"GET {path} HTTP/1.1\r\n"
            f"Host: {host}\r\n"
            "Upgrade: websocket\r\n"
            "Connection: Upgrade\r\n"
            f"Sec-WebSocket-Key: {sec_key}\r\n"
            "Sec-WebSocket-Version: 13\r\n\r\n"
        )
        self.sock.sendall(handshake.encode())

        header = self._read_until(b"\r\n\r\n")
        sec_accept = base64.b64encode(hashlib.sha1((sec_key + WS_GUID).encode()).digest()).decode()
        status_line = header.split(b"\r\n", 1)[0].decode(errors="replace")
        if b" 101 " not in header.split(b"\r\n", 1)[0] or sec_accept.encode() not in header:
            raise WebSocketError(f"WebSocket 握手失败：{status_line}")

    def _read_until(self, separator):
        while separator not in self.buffer:
            chunk = self.sock.recv(4096)
            if not chunk:
                raise WebSocketError("WebSocket 连接已关闭")
            self.buffer += chunk
        data, _, self.buffer = self.buffer.partition(separator)
        return data

    def _parse_frame(self):
        data = self.buffer
        if len(data) < 2:
            return None
        fin = bool(data[0] & 0x80)
        opcode = data[0] & 0x0F
        masked = bool(data[1] & 0x80)
        length = data[1] & 0x7F
        offset = 2
        if length == 126:
            if len(data) < offset + 2:
                return None
            length = struct.unpack("!H", data[offset:offset + 2])[0]
            offset += 2
        elif length == 127:
            if len(data) < offset + 8:
                return None
            length = struct.unpack("!Q", data[offset:offset + 8])[0]
            offset += 8
        mask = None
        if masked:
            if len(data) < offset + 4:
                return None
            mask = data[offset:offset + 4]
            offset += 4
        if len(data) < offset + length:
            return None
        payload = data[offset:offset + length]
        if mask:
            payload = bytes(byte ^ mask[i % 4] for i, byte in enumerate(payload))
        self.buffer = data[offset + length:]
        return fin, opcode, payload

    def _send_frame(self, opcode, payload):
        header = bytes([0x80 | opcode])
        if len(payload) < 126:
            header += bytes([0x80 | len(payload)])
        elif len(payload) < 65536:
            header += bytes([0x80 | 126]) + struct.pack("!H", len(payload))
        else:
            header += bytes([0x80 | 127]) + struct.pack("!Q", len(payload))
        mask = os.urandom(4)
        masked = bytes(byte ^ mask[i % 4] for i, byte in enumerate(payload))
        self.sock.sendall(header + mask + masked)

    def send_text(self, text):
        self._send_frame(0x1, text.encode("utf-8"))

    def recv_text(self):
        message = b""
        while True:
            frame = self._parse_frame()
            if frame is None:
                chunk = self.sock.recv(4096)
                if not chunk:
                    raise WebSocketError("WebSocket 连接已关闭")
                self.buffer += chunk
                continue
            fin, opcode, payload = frame
            if opcode == 0x8:
                code = struct.unpack("!H", payload[:2])[0] if len(payload) >= 2 else None
                reason = payload[2:].decode("utf-8", errors="replace")
                raise WebSocketError(f"WebSocket 连接已被服务端关闭（code={code}，reason={reason}）", code)
            if opcode == 0x9:
                self._send_frame(0xA, payload)
                continue
            if opcode == 0xA:
                continue
            if opcode in (0x1, 0x2):
                message = payload
            elif opcode == 0:
                message += payload
            else:
                continue
            if fin:
                return message.decode("utf-8", errors="replace")

    def close(self):
        try:
            self._send_frame(0x8, b"")
        except (OSError, WebSocketError):
            pass
        try:
            self.sock.close()
        except OSError:
            pass


def get_access_token(http, appid, secret):
    rep = http.post(
        f"{API_BASE}/app/getAppAccessToken",
        json={"appId": appid, "clientSecret": secret},
        timeout=15
    )
    try:
        data = rep.json()
    except ValueError:
        raise RuntimeError(f"获取 access_token 失败：HTTP {rep.status_code} {rep.text}")
    token = data.get("access_token")
    if not token:
        raise RuntimeError(f"获取 access_token 失败：{data}")
    return token


def get_gateway_url(http, access_token):
    rep = http.get(
        f"{API_BASE}/gateway",
        headers={"Authorization": f"QQBot {access_token}"},
        timeout=15
    )
    try:
        data = rep.json()
    except ValueError:
        raise RuntimeError(f"获取 WebSocket 网关失败：HTTP {rep.status_code} {rep.text}")
    url = data.get("url")
    if not url:
        raise RuntimeError(f"获取 WebSocket 网关失败：{data}")
    return url


def listen_for_openid(ws, access_token, deadline):
    ws.sock.settimeout(5)
    heartbeat_interval = 45.0
    last_seq = None
    last_heartbeat = time.time()
    while time.time() < deadline:
        try:
            payload = ws.recv_text()
        except socket.timeout:
            payload = None
        if payload is not None:
            data = json.loads(payload)
            op = data.get("op")
            if data.get("s") is not None:
                last_seq = data["s"]
            if op == 10:
                heartbeat_interval = data["d"]["heartbeat_interval"] / 1000
                ws.send_text(json.dumps({
                    "op": 2,
                    "d": {
                        "token": f"QQBot {access_token}",
                        "intents": C2C_INTENT,
                        "shard": [0, 1],
                        "properties": {}
                    }
                }))
                last_heartbeat = time.time()
            elif op == 0:
                event = data.get("t")
                if event == "READY":
                    print("鉴权成功，请使用手机QQ向机器人发送一条单聊消息")
                elif event == "C2C_MESSAGE_CREATE":
                    author = data.get("d", {}).get("author") or {}
                    openid = author.get("user_openid")
                    if openid:
                        return openid
            elif op in (7, 9):
                raise WebSocketError("网关要求重新连接")
        if time.time() - last_heartbeat >= heartbeat_interval:
            ws.send_text(json.dumps({"op": 1, "d": last_seq}))
            last_heartbeat = time.time()
    raise RuntimeError("等待单聊消息超时，请确认机器人已开通单聊权限并已添加为好友")


def wait_for_openid(gateway_url, access_token, timeout):
    deadline = time.time() + timeout
    while True:
        ws = None
        try:
            ws = WebSocketClient(gateway_url)
            return listen_for_openid(ws, access_token, deadline)
        except (OSError, WebSocketError, ValueError) as e:
            if isinstance(e, WebSocketError) and e.code in (4004, 4014):
                raise RuntimeError(f"网关拒绝连接：{e}（请确认机器人已开通单聊权限）") from e
            if time.time() >= deadline:
                raise RuntimeError("等待单聊消息超时，请确认机器人已开通单聊权限并已添加为好友") from e
            print(f"连接异常：{e}，2 秒后重新连接...")
            time.sleep(2)
        finally:
            if ws:
                ws.close()


def get_push_config_path():
    config_dir = os.getenv("AutoMihoyoBBS_push_path")
    if not config_dir:
        config_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "config")
    config_name = os.getenv("AutoMihoyoBBS_push_name") or "push.ini"
    return os.path.join(config_dir, config_name)


def read_qbot_config(path):
    cfg = ConfigParser(interpolation=None)
    cfg.read(path, encoding="utf-8")
    return (
        cfg.get("qbot", "appid", fallback="").strip(),
        cfg.get("qbot", "secret", fallback="").strip()
    )


def update_qbot_config(path, appid, secret, openid):
    with open(path, "r", encoding="utf-8", newline="") as f:
        raw = f.read()
    newline = "\r\n" if "\r\n" in raw else "\n"
    lines = raw.splitlines()
    values = {"appid": appid, "secret": secret, "openid": openid}

    section_start = None
    for index, line in enumerate(lines):
        if line.strip().lower() == "[qbot]":
            section_start = index
            break

    if section_start is None:
        if lines and lines[-1].strip():
            lines.append("")
        lines.extend([
            "# QQ机器人单聊推送",
            "# 单聊 OpenID 可通过 python qbot_get_openid.py 自动获取",
            "[qbot]"
        ])
        lines.extend(f"{key}={value}" for key, value in values.items())
    else:
        section_end = len(lines)
        for index in range(section_start + 1, len(lines)):
            if lines[index].strip().startswith("["):
                section_end = index
                break
        insert_at = section_end
        while insert_at > section_start + 1 and not lines[insert_at - 1].strip():
            insert_at -= 1
        remaining = dict(values)
        for index in range(section_start + 1, section_end):
            stripped = lines[index].strip()
            if not stripped or stripped.startswith(("#", ";")) or "=" not in stripped:
                continue
            key = stripped.split("=", 1)[0].strip().lower()
            if key in remaining:
                lines[index] = f"{key}={remaining.pop(key)}"
        for offset, (key, value) in enumerate(remaining.items()):
            lines.insert(insert_at + offset, f"{key}={value}")

    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(newline.join(lines) + newline)


def parse_args():
    parser = argparse.ArgumentParser(description="获取 QQ 机器人单聊 OpenID，并写入 push.ini")
    parser.add_argument("--appid", help="QQ 机器人 AppID，不填则读取配置或交互输入")
    parser.add_argument("--secret", help="QQ 机器人 AppSecret，不填则读取配置或交互输入")
    parser.add_argument("--timeout", type=int, default=300, help="等待单聊消息的超时时间（秒），默认 300")
    return parser.parse_args()


def main():
    args = parse_args()
    config_path = get_push_config_path()
    if not os.path.exists(config_path):
        print(f"配置文件不存在：{config_path}")
        return 1

    saved_appid, saved_secret = read_qbot_config(config_path)
    appid = (args.appid or saved_appid).strip()
    secret = (args.secret or saved_secret).strip()
    if not appid:
        appid = input("请输入 QQ 机器人 AppID: ").strip()
    if not secret:
        secret = getpass.getpass("请输入 QQ 机器人 AppSecret（输入时不显示）: ").strip()
    if not appid or not secret:
        print("AppID 和 AppSecret 不能为空")
        return 1

    http = get_new_session()
    try:
        print("正在获取 access_token...")
        access_token = get_access_token(http, appid, secret)
        print("正在获取 WebSocket 网关...")
        gateway_url = get_gateway_url(http, access_token)
        print("正在连接 QQ 机器人网关...")
        openid = wait_for_openid(gateway_url, access_token, args.timeout)
    except Exception as e:
        print(f"获取单聊 OpenID 失败：{e}")
        return 1

    print(f"已获取单聊 OpenID：{openid}")
    update_qbot_config(config_path, appid, secret, openid)
    print(f"APPID、appsecret 和单聊 OpenID 已写入 {config_path}")
    print("请将 push.ini 中 [setting] 的 push_server 设置为 qbot，并按需设置 enable=true")
    return 0


if __name__ == "__main__":
    sys.exit(main())
