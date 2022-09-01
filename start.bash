#!/bin/bash
# 进入脚本所在目录
cd $(cd `dirname $0`;pwd)
# 随机延时$RANDOM值为1~32767
sleep $[$RANDOM%1200];
python ./main.py;
