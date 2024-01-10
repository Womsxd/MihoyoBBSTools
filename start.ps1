# Windows 下的每日自动签到脚本，每天电脑开机时即可自动签到，几乎没有后台占用；
# 一般情况下只要电脑本日内开机过，即可自动签到，且可以识别本日是否签到，减少无效签到操作；
# 脚本可以设置多个时间执行签到任务，并检测当日是否签到，若已经签到则跳过此次任务。

# 当且仅当执行时间或开机自动签到进行了修改时，需要在 此电脑 -> 管理 -> 
# 计划任务程序 —> 删除(MihoyoDailyTask) -> 重新运行脚本

# 前置任务：
# 1.保证 main.py/main_multi.py 可以正常运行
# 2.（非必须）设置captcha.py，实现自动打码（自动验证码）；如果没有游戏每日签到成功率很低。
# captcha.py 配置示例：
# def game_captcha(gt: str, challenge: str):
#     rep = http.post(
#         url="http://www.xxxx.com", （搜索打码平台）
#         data={
#             "appkey": "******************************",
#             "gt": gt,
#             "challenge": challenge,
#             "referer": "https://api-takumi.mihoyo.com/event/bbs_sign_reward/sign",
#         },
#     ).json()
#     return rep["data"]["validate"] 
# def bbs_captcha(gt: str, challenge: str):
#     return game_captcha(gt, challenge)
#
# 3. 使用powershell运行脚本，Win+R 弹出窗口中输入 powershell.exe,
# 输入本脚地址（~\MihoyoBBSTools\start.ps1）运行即可长期自动运行。（电脑可以自由开关机）
#-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*#



# 设置任务计划程序名称
$taskName = "MihoyoDailyTask"

# 是否定时执行
$excuteOnSchedule = $true

# 设置执行的时间列表，可以自己删减脚本触发时间
$executionTimes = @("00:01", "08:00", "12:00", "15:00", "18:00", "20:00")

# 开机时是否自动运行一次任务
$executeOnStartup = $true

# 使用main_multi.py时，设置为true
$multiConfig = $false

# 获取脚本自身的路径
$scriptPath = $MyInvocation.MyCommand.Path

# 获取根目录
$rootDirectory = Split-Path -Path $scriptPath -Parent

# 设置日志文件目录
$logDir = Join-Path -Path $rootDirectory -ChildPath "logs"

# 检查日志文件目录是否存在
if (-not (Test-Path -Path $logDir -PathType Container)) {
    # 如果目录不存在，则创建目录
    New-Item -ItemType Directory -Path $logDir -Force
    # 指示Git忽略目录文件
    "*" | Out-File -FilePath "$logDir\.gitignore" -Encoding utf8
}

# python.exe 的地址
$pythonAddr = "python3"

$PythonFile = Join-Path -Path $rootDirectory -ChildPath ($multiConfig ? "main_multi.py" : "main.py")

# 设置执行的命令
$commandToExecute = "$pythonAddr $pythonFile"

# 获取当天日期
$today = Get-Date -Format "yyyyMMdd"

# 获取当天的日志文件地址
$logFileName = "log_$today.log"
$logPath = Join-Path -Path $logDir -ChildPath $logFileName
$logExists = Test-Path $logPath

# 检查是否存在任务计划程序
$taskExists = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue

function Logger {
    param 
    (
        [string]$Level,
        [string]$Message
    )

    $timeStamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"

    $logEntry = "$timeStamp [$Level] $Message"

    $logFile = $logPath

    Add-Content -Path $logFile -Value $logEntry
    Write-Host $logEntry
}

Logger -Message "尝试注册任务计划程序..." -Level "INFO"

if (-not $taskExists) {
    # 创建任务计划程序触发器
    $timedTriggers = foreach ($time in $executionTimes) {
        New-ScheduledTaskTrigger -Daily -At $time
    }

    # 添加在系统开机2分钟后运行的触发器
    $delayedTrigger = New-ScheduledTaskTrigger -AtStartup -RandomDelay (New-TimeSpan -Minutes 2)

    if (-not($excuteOnSchedule -or $executeOnStartup)) {
        Logger -Message "定时触发器和启动触发器以取消，定时任务失效！" -Level "WARN"
        Exit
    }

    if ($excuteOnSchedule) {
        $triggers += $timedTriggers
    }

    if ($executeOnStartup) {
        $triggers += $delayedTrigger 
    }

    $action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument $scriptPath

    $taskRegistered = Register-ScheduledTask -TaskName $taskName -Trigger $triggers -Action $action -Description "Run MihoyoDailyTask Script."

    if ($taskRegistered) {
        Logger -Message "$taskName 注册成功~" -Level "INFO"
    }
    else {
        Logger -Message "$taskName 注册失败~" -Level "ERROR"
        # 检查是否以管理员权限运行，如果不是则提升权限
        if (-not ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
            Logger -Message "请以管理员身份运行此脚本！" -Level "WARN"
            Start-Sleep -Seconds 1
            Start-Process powershell.exe -Verb RunAs -ArgumentList ("-File", $scriptPath)
            Exit
        }
    }
}
else {
    Logger -Message "$taskName 已注册！" -Level "INFO"
}

# 检查网络连接
$connected = Test-Connection -ComputerName "www.miyoushe.com" -Count 2 -Quiet

if (-not $connected) {
    Logger -Level "ERROR" -Message "网络异常，此次任务执行失败！"
    Exit
}


$overFlag = "*FLAG*"
if ((-not(($logExists ) -and ((Get-Content $logPath -Tail 10) -like $overFlag)))) {
    Logger -Level "INFO" -Message "开始执执行签到任务..."
    Logger -Level "INFO" -Message "执行命令行：& $commandToExecute"
    Invoke-Expression -Command "$commandToExecute 2>&1" | Tee-Object -FilePath $logPath
    Logger -Level "INFO" -Message "签到任务完成!"
}
else {
    Logger -Level "INFO" -Message "今日签到已完成，本次任务跳过!"
}

Logger -Level "INFO" -Message "FLAG"