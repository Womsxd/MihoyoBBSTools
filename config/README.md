# Config配置教程

## 本项目识别config文件的方法

单用户是直接读取文件夹里面的`config.json`，多用户是读取文件夹里面为`.json`为拓展名的文件

## json文件的字段讲解

```json
"enable_Config": true,
```

>此字段的作用是是否启用这个配置文件，`bool`类型，可设置`true`(默认)和`false`

```json
"config_Version": 5,
```

>此字段的作用是表明配置文件版本(4会被转成5)，`int`类型

```json
"mihoyobbs_Login_ticket": "", 
```

>此字段的作用存储米游社需要的cookie值(你填入的cookie里面必须带这个)，`str`类型，默认为空，脚本执行成功时自动填入

```json
"mihoyobbs_Stuid": "",
```

>此字段的作用存储米游社需要的cookie值(实际上就是uid)，`str`类型，默认为空，脚本执行成功时自动获取并填入

```json
"mihoyobbs_Stoken": "", 
```

>此字段的作用存储米游社的cookie值，`str`类型，默认为空，脚本执行成功时自动获取并填入

```json
"mihoyobbs_Cookies": "", 
```

>此字段的作用存储米游社的cookie值(用于获取上面两个参数和后续的原神&崩坏3自动签到)，`str`类型，默认为空，脚本执行前必须填入

```json
"mihoyobbs": {
    "enable": true, 
    "checkin": true, 
    "checkin_multi": true, 
    "checkin_multi_list": [2, 5], 
    "read_posts": true, 
    "like_posts": true, 
    "un_like": true, 
    "share_post": true
}, 
```

此字段的作用是米游币获取相关的设置，`object`类型(**python**里面是`dict`)

>`enable`的作用是是否启用米游币获取，`bool`类型，可设置`true`(默认)和`false`
>
>`checkin`的作用是是否启用讨论区自动签到，`bool`类型，可设置`true`(默认)和`false`
>
>`checkin_multi`的作用是是否启用多个讨论区签到(关闭的话只签到大别墅)，`bool`类型，可设置`true`(默认)和`false`
>
>`checkin_multi_list`的作用设置要签到的讨论区，`array`类型(**python**里面是`list`)，可设置内容可以设置`[1,2,3,4,5]`签到全部讨论区，默认是`[2,5]`，可以通过调整id的位置来进行设置阅读/点赞/分享指定讨论区的帖子`[2,1,5]`（签到原神，崩坏3和大别墅）[讨论区的id对应关系](## 讨论区的id对应关系)
>
>`read_posts`的作用是是否启用自动阅读帖子，`bool`类型，可设置`true`(默认)和`false`
>
>`like_posts`的作用是是否启用自动点赞帖子，`bool`类型，可设置`true`(默认)和`false`
>
>`un_like`的作用是是否启用自动取消帖子点赞(当`like_posts`为`false`时本设置无效)，`bool`类型，可设置`true`(默认)和`false`
>
>`share_post`的作用是是否启用自动分享帖子，`bool`类型，可设置`true`(默认)和`false`

```json
"genshin_Auto_sign": true,
```

>此字段的作用是是否启用原神自动签到，`bool`类型，可设置`true`(默认)和`false`

```json
"honkai3rd_Auto_sign": false
```

>此字段的作用是是否启用崩坏3自动签到，`bool`类型，可设置`true`和`false`(默认)

## 讨论区的id对应关系

`1`对应崩坏3

`2`对应原神

`3`对应崩坏学园2

`4`对应未定事件簿

`5`对应大别墅

`6`对应崩坏：星穹铁道


# push.ini配置教程

* push_server 可选范围 cqhttp ftqq(sever酱) pushplus telegram dingrobot bark


## Wecom
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

## dingrobot
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



## bark

一款开源的消息推送工具 https://github.com/Finb/Bark

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

