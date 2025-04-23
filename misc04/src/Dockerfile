FROM golang:1.23-alpine AS builder

WORKDIR /app

COPY go.mod go.sum main.go ./

RUN go mod tidy

RUN go build -o main .

FROM alpine:latest

WORKDIR /app

COPY --from=builder /app/main .

CMD ["./main"]
