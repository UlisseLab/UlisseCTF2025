FROM ubuntu:noble

RUN apt update && apt upgrade -y
RUN apt install -y imagemagick python3-pip python3-venv
RUN python3 -m venv snappy-venv
RUN bash -c 'source ./snappy-venv/bin/activate && pip3 install python-snappy==0.7.3'

ENV FLAG ulissectf{...}

CMD convert -size 800x800 xc:white -gravity North -pointsize 30 -annotate +0+100 "$FLAG" /tmp/img.jpg; \
    bash -c 'source ./snappy-venv/bin/activate && python3 -m snappy -c /tmp/img.jpg > /tmp/flag.data'; \
    sed 's/sNaPpY/s\x00a\x00p\x00/' < /tmp/flag.data > /challenge/attachments/flag.data
