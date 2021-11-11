# 米游社辅助签到

基于Python3的米游社辅助签到项目

本项目米游币部分参考[XiaoMiku01/miyoubiAuto](https://github.com/XiaoMiku01/miyoubiAuto)进行编写

* 此项目的用途

  这是一个米游社的辅助签到项目，包含了米游币和原神以及崩坏3

## 如何使用程序

* **部署方法**

  1. 使用[Git](https://git-scm.com/)或[点击此处](https://github.com/Womsxd/AutoMihoyoBBS/archive/refs/heads/master.zip)下载本项目

  2. 下载[Python3](https://www.python.org/downloads/)

  3. 解压本项目压缩包,在解压目录中**Shift+右键** 打开你的命令提示符cmd或powershell

  4. [requirements.txt](https://raw.githubusercontent.com/Womsxd/AutoMihoyoBBS/master/requirements.txt) 是所需第三方模块，执行 `pip install -r requirements.txt` 安装模块

  5. 打开目录中的**config文件夹**复制`config.json.example`并改名为`config.json`，脚本的多用户功能靠读取不同的配置文件实现，你可以创建无数个`自定义名字.json`，脚本会扫描**config**目录下`json`为拓展名的文件，并按照名称顺序依次执行。

  6. 请使用vscode/notepad++等文本编辑器打开上一步复制好的配置文件

  7. **使用[获取Cookie](#获取米游社Cookie)里面的方法来获取米游社Cookie**

  8. 将复制的Cookie粘贴到`config.json`的`"mihoyobbs_Cookies":" "`中

        例子

        > ```json
        > "mihoyobbs_Cookies": "你复制的cookie"
        > ```

  9. 在命令提示符(cmd)/powershell，输入`python main.py`来进行执行
  
  10. 多用户的请使用`python main_multi.py`，多用户在需要自动执行的情况下请使用`python main_multi.py autorun`

## 获取米游社Cookie

1. 打开你的浏览器,进入**无痕/隐身模式**

2. 由于米哈游修改了bbs可以获取的Cookie，导致一次获取的Cookie缺失，所以需要增加步骤

3. 打开`http://bbs.mihoyo.com/ys/`并进行登入操作

4. 在上一步登入完成后新建标签页，打开`http://user.mihoyo.com/`并进行登入操作

5. 按下键盘上的`F12`或右键检查,打开开发者工具,点击Console

6. 输入

   ```javascript
   var cookie=document.cookie;var ask=confirm('Cookie:'+cookie+'\n\nDo you want to copy the cookie to the clipboard?');if(ask==true){copy(cookie);msg=cookie}else{msg='Cancel'}
   ```

   回车执行，并在确认无误后点击确定。

7. **此时Cookie已经复制到你的粘贴板上了**


## 使用Docker运行

Docker的运行脚本基于Linux平台编写，暂未在Win平台测试。

将本项目Clone至本地后，请先按照上述步骤添加或修改配置文件。随后运行`make-docker.sh`脚本本地构建Docker镜像，同时初次运行容器。

```shell
sh make-docker.sh
```

或手动执行

```
# 编译容器
docker build -f Dockerfile --tag ${docker_name}:"${time_now}" .
```

```
# 运行容器（默认自动多配置文件）
docker run -itd \
	--name ${docker_name} \
	--log-opt max-size=1m \
	-v $(pwd):/var/app \
	${docker_name}:"${time_now}"
# 运行容器（直接运行main.py）
docker run -itd \
	--name ${docker_name} \
	--log-opt max-size=1m \
	-v $(pwd):/var/app \
	-e MULTI=FALSE \
	${docker_name}:"${time_now}"
```

若需要添加配置文件或修改配置文件，可直接在主机config文件夹中修改，修改的内容将实时同步在容器中。

若需要再次运行签到脚本，可手动重启容器。每次运行Docker容器后，容器内将自动按照参数执行签到活动，签到完成后容器将自动停止运行。

```
docker restart ${docker_name} && docker logs -f ${docker_name}
```

关于每日定时，用户可在容器外部设计定时触发（启动）程序，每日定时运行脚本。

（若有需要可自行编写相关脚本通知完成状态

## 使用的第三方库

requests: [github](https://github.com/psf/requests) [pypi](https://pypi.org/project/requests/)

httpx: [github](https://github.com/encode/httpx) [pypi](https://pypi.org/project/httpx/)

## 关于使用 Github Actions 运行

本项目**不支持**也**不推荐**使用`Github Actions`来每日自动执行！

也**不会**处理使用`Github Actions`执行有关的issues！

推荐使用 阿里云/腾讯云 的云函数来进行每日自动执行脚本。

## License

[MIT License](https://github.com/Womsxd/AutoMihoyoBBS/blob/master/LICENSE)

## 鸣谢

[JetBrains](https://jb.gg/OpenSource)
