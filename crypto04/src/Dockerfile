FROM ubuntu@sha256:ed1544e454989078f5dec1bfdabd8c5cc9c48e0705d07b678ab6ae3fb61952d2

RUN apt-get update && \
    apt-get install -y ca-certificates curl gnupg gnupg2 libc6 python3 python3-pip xinetd bsdmainutils bc iproute2 iputils-ping docker.io && \
    pip3 install flask docker web3

WORKDIR /app
RUN useradd -m bridge
RUN mkdir -p /home/bridge/app
RUN mkdir contracts 
RUN mkdir offchain
COPY orchestrator.py .
COPY entrypoint.sh .
COPY contracts contracts
COPY offchain offchain

RUN chmod +x /app/entrypoint.sh
ENTRYPOINT ["/app/entrypoint.sh"]
