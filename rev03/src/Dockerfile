FROM zephyrprojectrtos/zephyr-build:v0.27.4

ENV FLAG ulissectf{...}

USER root
RUN apt update
RUN apt install -y --no-install-recommends vim git cmake ninja-build gperf \
                                           ccache dfu-util device-tree-compiler wget \
                                           python3-dev python3-pip python3-setuptools python3-tk python3-wheel xz-utils file \
                                           make gcc gcc-multilib g++-multilib libsdl2-dev libmagic1

ADD https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh /usr/local/bin/install.sh

RUN chmod +x /usr/local/bin/install.sh && /usr/local/bin/install.sh
RUN bash -c 'source ~/.nvm/nvm.sh && nvm install 22'

RUN mkdir /zephyr
RUN cd /zephyr && west init
ENV ZEPHYR_BASE /zephyr/zephyr
RUN pip3 install -r /zephyr/zephyr/scripts/requirements.txt
RUN cd /zephyr/zephyr && west sdk install
RUN cd /zephyr && west update

CMD cp -rav /challenge/src/firmware /zephyr/zephyr/firmware ; \
    cd /zephyr/zephyr/firmware ; \
    bash -x scripts/generate-firmware.sh && \
    cp build/firmware/zephyr/zephyr.elf /challenge/attachments/zephyr.elf && \
    chown 1000:1000 /challenge/attachments/zephyr.elf && \
    /opt/toolchains/zephyr-sdk-0.17.0/xtensa-espressif_esp32_zephyr-elf/xtensa-espressif_esp32_zephyr-elf/bin/strip /challenge/attachments/zephyr.elf

