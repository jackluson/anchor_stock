
# FROM scratch
FROM python3.8.11-slim-base

RUN pip install beautifulsoup4==4.9.3
RUN pip install lxml==4.9.1
