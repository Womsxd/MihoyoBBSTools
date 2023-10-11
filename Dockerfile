FROM python:3-alpine
LABEL maintainer="x.yangtze.river@gmail.com"

ENV CRON_SIGNIN='30 9 * * *'
ENV MULTI=TRUE
ENV TZ=Asia/Shanghai
# RUN sed -i 's/dl-cdn.alpinelinux.org/mirrors.tuna.tsinghua.edu.cn/g' /etc/apk/repositories
RUN apk add --no-cache tzdata

WORKDIR /tmp
ADD requirements.txt ./
# RUN pip3 install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt
RUN pip3 install -r requirements.txt 

WORKDIR /var/app
COPY . /var/app

CMD ["python3", "./docker.py" ]
