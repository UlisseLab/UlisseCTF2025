FROM ctsrd/cheribsd-qemu-riscv64-purecap@sha256:966000f5e8cdcc77102b140f4aa3a68166a8b855c4d69cab838004de61b4e751

ENV FLAG flag{test}
# Port of the TCP challenge
ENV PORT 5534
# Root password in the machine (crypt generated)
ENV PASSWORD $6$xeeleereez7ahfah$6p6o.sXyGYHh7MLJ1g2M21qaes9.c05neUOEaU/4rVicY2g04l9jDqPbSGTbYf.ZUbil04YP3BdhfxaYOct10

COPY entrypoint.sh /usr/local/bin/entrypoint.sh
RUN sudo chmod +x /usr/local/bin/entrypoint.sh

RUN sudo apt update && sudo apt install -y socat

CMD /usr/local/bin/entrypoint.sh
