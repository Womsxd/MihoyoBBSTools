FROM python:3-alpine
LABEL maintainer="mailto@wolfbolin.com"

ENV CRON_SIGNIN='30 9 * * *'
ENV MULTI=TRUE
ENV TZ=Asia/Shanghai
RUN adduser app -D
RUN sed -i 's/dl-cdn.alpinelinux.org/mirrors.tuna.tsinghua.edu.cn/g' /etc/apk/repositories \
	&& apk add --no-cache tzdata

WORKDIR /tmp
ADD requirements.txt ./
RUN pip3 install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt 

USER app
WORKDIR /var/app
COPY . /var/app

CMD ["python3", "./docker.py" ]
