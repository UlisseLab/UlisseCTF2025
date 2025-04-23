FROM emscripten/emsdk@sha256:5aea37132ad0827908065a5d7432d2f4048011dce7169aa1ab3441b0720312e2 AS builder

COPY . /src
WORKDIR /src

RUN --mount=type=secret,id=flag,env=FLAG \
    ./generate_problem.sh $FLAG


FROM nginx:1.21.1@sha256:9d6b58feebd2dbd3c56ab5853333d627cc6e281011cfd6050fa4bcf2072c9496

WORKDIR /usr/share/nginx/html
RUN rm -rf ./*

COPY index.html .
COPY --from=builder /src/check.js /src/check.wasm ./

CMD ["nginx", "-g", "daemon off;"]
