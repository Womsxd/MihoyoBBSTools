FROM python:3.12-alpine
LABEL maintainer="x.yangtze.river@gmail.com"

ENV CRON_SIGNIN='30 9 * * *'
ENV MULTI=TRUE
ENV TZ=Asia/Shanghai

WORKDIR /app
COPY . /app

# RUN apk add --no-cache tzdata && pip3 --no-cache install -r requirements.txt
RUN sed -i 's/dl-cdn.alpinelinux.org/mirrors.tuna.tsinghua.edu.cn/g' /etc/apk/repositories \
&& apk add --no-cache tzdata \
&& pip3 --no-cache install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt

CMD ["python3", "./docker.py" ]
