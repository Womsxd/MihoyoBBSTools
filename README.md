# 米游社辅助签到

基于Python3的米游社辅助签到项目

本项目米游币部分参考[XiaoMiku01/miyoubiAuto](https://github.com/XiaoMiku01/miyoubiAuto)进行编写

* 此项目的用途

  这是一个米游社的辅助签到项目，包含了米游币、崩坏2、崩坏3、原神，后续会支持未定事件簿

## 如何使用程序

* **部署方法**

  1. 使用[Git](https://git-scm.com/)或[点击此处](https://github.com/Womsxd/AutoMihoyoBBS/archive/refs/heads/master.zip)下载本项目

  2. 下载[Python3](https://www.python.org/downloads/)

  3. 解压本项目压缩包,在解压目录中**Shift+右键** 打开你的命令提示符cmd或powershell

  4. [requirements.txt](https://raw.githubusercontent.com/Womsxd/AutoMihoyoBBS/master/requirements.txt) 是所需第三方模块，执行 `pip install -r requirements.txt` 安装模块

  5. 打开目录中的**config文件夹**复制`config.json.example`并改名为`config.json`，脚本的多用户功能靠读取不同的配置文件实现，你可以创建无数个`自定义名字.json`，脚本会扫描**config**目录下`json`为拓展名的文件，并按照名称顺序依次执行。

  6. 请使用vscode/notepad++等文本编辑器打开上一步复制好的配置文件

  7. **使用[获取Cookie](#获取米游社Cookie)里面的方法来获取米游社Cookie**

  8. 将复制的Cookie粘贴到`config.json`的`"cookie":" "`中(在`account`里面)

        例子

        > ```json
        > "cookie": "你复制的cookie"
        > ```

  9. 在命令提示符(cmd)/powershell，输入`python main.py`来进行执行
  
  10. 多用户的请使用`python main_multi.py`，多用户在需要自动执行的情况下请使用`python main_multi.py autorun`

## 获取米游社Cookie

1. 打开你的浏览器,进入**无痕/隐身模式**

2. 由于米哈游修改了bbs可以获取的Cookie，导致一次获取的Cookie缺失，所以需要增加步骤

3. 打开`http://bbs.mihoyo.com/ys/`并进行登入操作

4. 在上一步登入完成后新建标签页，打开`http://user.mihoyo.com/`并进行登入操作 (如果你不需要自动获取米游币可以忽略这个步骤，并把`mihoyobbs`的`enable`改为`false`即可)

5. 按下键盘上的`F12`或右键检查,打开开发者工具,点击Console

6. 输入

   ```javascript
   var cookie=document.cookie;var ask=confirm('Cookie:'+cookie+'\n\nDo you want to copy the cookie to the clipboard?');if(ask==true){copy(cookie);msg=cookie}else{msg='Cancel'}
   ```

   回车执行，并在确认无误后点击确定。

7. **此时Cookie已经复制到你的粘贴板上了**

## 使用Docker运行

Docker的运行脚本基于Linux平台编写，暂未在Win平台测试。

将本项目Clone至本地后，请先按照上述步骤添加或修改配置文件。随后执行

```text
docker-compose up -d
```

启动docker容器。  
&nbsp;  
容器运行成功后可用

```text
docker-compose logs -f
```

命令来查看程序输出。  
&nbsp;  
若需要添加配置文件或修改配置文件，可直接在主机config文件夹中修改，修改的内容将实时同步在容器中。

每次运行Docker容器后，容器内将自动按照参数执行签到活动，签到完成后容器将默认在每天上午9:30运行一次，如果想自行修改时间可自行编辑`docker-compose.yml`文件中的`CRON_SIGNIN`，将其修改成想运行的时间。

## 使用云函数运行

腾讯云函数服务免费额度近期有变化，为了**避免产生费用**，建议切换到阿里云 函数计算 FC

* 腾讯云

1. 在本地完整运行一次。

2. 打开并登录[云函数控制台](https://console.cloud.tencent.com/scf/list)。

3. 新建云函数 - 自定义创建，函数类型选`事件函数`，部署方式选`代码部署`，运行环境选 `Python3.6`.

4. 提交方法选`本地上传文件夹`，并在下方的函数代码处上传整个项目文件夹。

5. 执行方法填写 `index.main_handler`,多用户请填写`index.main_handler_mulit`.

6. 展开高级配置，将执行超时时间修改为 `300 秒`，其他保持默认。

7. 展开触发器配置，选中自定义创建，触发周期选择`自定义触发周期`，并填写表达式`0 0 10 * * * *`（此处为每天上午 10 时运行一次，可以自行修改）

8. 完成，enjoy it！

* 阿里云

  1. 在本地完整运行一次。
  2. 打开并登录[函数计算 FC](https://fcnext.console.aliyun.com/cn-hangzhou/services)。注意左上方显示的地区，可点击切换其他地区。
  3. 创建服务 （日志功能可能产生费用，建议关闭）
     1. 创建函数
     2. 从零开始创建
        1. `请求处理程序类型：处理事件请求`
        2. `请求处理程序：index.main_handler`，多用户请填写`index.main_handler_mulit`
        3. 配置触发器：触发器类型 定时触发器 异步调用。建议触发方式设为`指定时间`
        4. 点击创建
     3. 进入函数详情
        1. 打开函数配置
        2. 修改 `环境信息` - `执行超时时间` 为300秒。
  4. 测试运行
     1. 打开 `函数详情`
     2. 点击`测试函数`
  5. 完成

## 使用的第三方库

requests: [github](https://github.com/psf/requests) [pypi](https://pypi.org/project/requests/)

httpx: [github](https://github.com/encode/httpx) [pypi](https://pypi.org/project/httpx/)

crontab: [github](https://github.com/josiahcarlson/parse-crontab) [pypi](https://pypi.org/project/crontab/)

## 关于使用 Github Actions 运行

本项目**不支持**也**不推荐**使用`Github Actions`来每日自动执行！

也**不会**处理使用`Github Actions`执行有关的issues！

推荐使用 阿里云/腾讯云 的云函数来进行每日自动执行脚本。

## Stargazers over time

[![Stargazers over time](https://starchart.cc/Womsxd/AutoMihoyoBBS.svg)](https://starchart.cc/Womsxd/AutoMihoyoBBS)

## License

[MIT License](https://github.com/Womsxd/AutoMihoyoBBS/blob/master/LICENSE)

## 鸣谢

[JetBrains](https://jb.gg/OpenSource)
