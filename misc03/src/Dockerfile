FROM alpine:latest AS build
RUN apk add --no-cache gcc musl-dev openssl-dev openssl

WORKDIR /build
COPY challenge.c server.c
RUN gcc -DFLAG="\"UlisseCTF{s3nd5_c4n_b3_bl0ck1ng_t00!}\"" -o server server.c -lssl -lcrypto

FROM alpine:latest
RUN apk add --no-cache openssl
COPY --from=build /build/server /app/server

EXPOSE 8080
CMD ["/app/server", "8080"]
