# list of alpine packages: https://pkgs.alpinelinux.org/packages
FROM alpine

RUN apk update && apk add --no-cache \
    bash \
    curl \
    jq

RUN curl -Sf https://temporal.download/cli.sh | sh

ENV PATH="/root/.temporalio/bin:${PATH}"

RUN echo "Temporal CLI version: $(temporal --version)"

EXPOSE 7233
EXPOSE 8080

ENTRYPOINT ["temporal", "server", "start-dev", "--ui-port", "8080", "--ip", "0.0.0.0"]

