FROM ubuntu:latest
RUN apt-get update && \
    apt-get install -y python \
                       libpq-dev \
                       libjpeg-dev \
                       libfreetype6-dev \
                       python-dev \
                       python-pip \
    && apt-get clean \
    && apt-get autoclean \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

ADD . /app
RUN cd /app; pip install -r requirements.txt
WORKDIR /app

ENV LEANCLOUD_APP_ID test_app_id
ENV LEANCLOUD_APP_KEY test_app_key

RUN python db_store.py
CMD ["python", "/app/wechat_group_bot.py"]
