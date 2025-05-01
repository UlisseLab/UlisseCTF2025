FROM ctsrd/cheribsd-sdk-qemu-riscv64@sha256:247a65f24ccabf5eb2a25a50f4aac0c28cb92c9e54b47896232e87c94c0496a5

CMD mkdir /tmp/output && \
    cp /challenge/src/compile/cheri-challenge.c /tmp/output && \
    cp /challenge/src/compile/Makefile /tmp/output && \
    cd /tmp/output && make && \
    sudo cp cheri-challenge /challenge/attachments/.
