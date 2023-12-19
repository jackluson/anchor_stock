#基础镜像
# FROM python3.8.11-base:latest
FROM python3.8.11-slim-base

LABEL description="A docker image for anchor_stock"

RUN mkdir /anchor_stock
COPY .  /anchor_stock

# 设置工作目录文件夹
WORKDIR /anchor_stock

# RUN apt-get update && apt-get upgrade 
# RUN apt-get install gcc
# RUN apt-get update \
#     && apt-get upgrade  \
#     && apt-get install libc-dev -y \
#     && apt-get install libatlas-base-dev -y
# 安装依赖
# https://tehub.com/a/aCPSEYAtml -- Docker Alpine apk设置国内源
# https://furthergazer.top/article/2020/3/9/7.html -- Docker Alpine apk设置国内源

# RUN apk add gcc musl-dev libffi-dev openssl-dev cargo
# RUN pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/
RUN pip install beautifulsoup4==4.9.3
CMD ["python", "-u", "task.py"]
