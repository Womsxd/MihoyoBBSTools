# Config配置教程

## 本项目识别config文件的方法

单用户是直接读取文件夹里面的`config.json`，多用户是读取文件夹里面为`.json`为拓展名的文件

## json文件的字段讲解

```json
"enable_Config": true,
```

>此字段的作用是是否启用这个配置文件，`bool`类型，可设置`true`(默认)和`false`

```json
"config_Version": 3,
```

>此字段的作用是表明配置文件版本(不过脚本里面暂时没有用到)，`int`类型

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
    "bbs_Global": true, 
    "bbs_Signin": true, 
    "bbs_Signin_multi": true, 
    "bbs_Signin_multi_list": [2, 5], 
    "bbs_Read_posts": true, 
    "bbs_Like_posts": true, 
    "bbs_Unlike": true, 
    "bbs_Share": true
}, 
```

此字段的作用是米游币获取相关的设置，`object`类型(**python**里面是`dict`)

>`bbs_Global`的作用是是否启用米游币获取，`bool`类型，可设置`true`(默认)和`false`
>
>`bbs_Signin`的作用是是否启用讨论区自动签到，`bool`类型，可设置`true`(默认)和`false`
>
>`bbs_Signin_multi`的作用是是否启用多个讨论区签到(关闭的话只签到大别墅)，`bool`类型，可设置`true`(默认)和`false`
>
>`bbs_Signin_multi_list`的作用设置要签到的讨论区，`array`类型(**python**里面是`list`)，可设置内容可以设置`[1,2,3,4,5]`签到全部讨论区，默认是`[2,5]`，可以通过调整id的位置来进行设置阅读/点赞/分享指定讨论区的帖子`[2,1,5]`（签到原神，崩坏3和大别墅）[讨论区的id对应关系](## 讨论区的id对应关系)
>
>`bbs_Read_posts`的作用是是否启用自动阅读帖子，`bool`类型，可设置`true`(默认)和`false`
>
>`bbs_Like_posts`的作用是是否启用自动点赞帖子，`bool`类型，可设置`true`(默认)和`false`
>
>`bbs_Unlike`的作用是是否启用自动取消帖子点赞(当`bbs_Like_posts`为`false`时本设置无效)，`bool`类型，可设置`true`(默认)和`false`
>
>`bbs_Share`的作用是是否启用自动分享帖子，`bool`类型，可设置`true`(默认)和`false`

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
