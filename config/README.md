# Config配置教程

## 本项目识别config文件的方法

单用户是直接读取文件夹里面的`config.yaml`，多用户是读取文件夹里面为`.yaml`为拓展名的文件

## 讨论区的id对应关系

`1`对应崩坏3

`2`对应原神

`3`对应崩坏学园2

`4`对应未定事件簿

`5`对应大别墅

`6`对应崩坏：星穹铁道

`8`对应绝区零

## push.ini配置教程

* push_server 可选范围 cqhttp ftqq(sever酱) pushplus telegram dingrobot bark qbot

### Wecom

企业微信

**wechat_id**填写**企业ID**，见:  我的企业 -> 企业设置 -> 企业ID

**agentid**填写**AgentId**，见:  应用管理 -> 自建 -> 「你自己的应用」 -> 复制数字
**secret**填写**Secret**，见:  应用管理 -> 自建 -> 「你自己的应用」->  点<u>查看</u>链接

**touser**填写**接收人**，默认 @all 通知企业内所有人，指定接收人时使用大驼峰拼音，多个可用｜隔开

填写示例

```ini
[setting]
enable=true
push_server=wecom

[wecom]
#企业微信的corpid
wechat_id=
#企业微信的应用配置
agentid=
secret=
touser=@all
```

### dingrobot

钉钉群机器人

**webhook**填写**Webhook**地址

**secret**填写**安全设置**中**加签**的密钥，此选项为可选项

填写示例

```ini
[setting]
enable=true
push_server=dingrobot

[dingrobot]
webhook=https://oapi.dingtalk.com/robot/send?access_token=XXX
secret=
```

### bark

一款开源的消息推送工具 [Bark](https://github.com/Finb/Bark)

手机安装bark客户端获得托管在api.day.app的Token，也可以自己搭建私有服务端。

**api_url**一般不用改，自己搭建私有服务端的需要改掉

**token**填写**APP**内**URL**中的密钥，此选项必填

> `https://api.day.app/` `token部分` `/Title/NotificationContent`

填写示例

```ini
[setting]
enable=true
push_server=bark

[bark]
api_url=https://api.day.app
token=XXX
```

### qbot

QQ 机器人单聊推送，需要在 [QQ 开放平台](https://q.qq.com/) 创建机器人并开通单聊权限。

**appid** / **secret** 在开放平台「开发设置」中获取

**openid** 是单聊用户的 OpenID，可运行 `python qbot_get_openid.py`，按提示获取 APPID、AppSecret 后，用手机 QQ 向机器人发送一条消息即可自动获取，并自动写入 `config/push.ini`

注意：机器人发送的是主动消息，如果用户在 QQ 客户端关闭了「允许主动发送」，推送会失败。

填写示例

```ini
[setting]
enable=true
push_server=qbot

[qbot]
appid=102000001
secret=XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
openid=XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```
