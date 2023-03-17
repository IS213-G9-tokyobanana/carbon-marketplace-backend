# argument passed from docker-compose.yml with default value of empty string
ARG private_registry_uri= 

# list of alpine packages: https://pkgs.alpinelinux.org/packages
FROM ${private_registry_uri}alpine:3.10

RUN apk add --no-cache bash curl wget

RUN apk add --no-cache python3 && \
    python3 -m ensurepip && \
    rm -r /usr/lib/python*/ensurepip && \
    if [[ ! -e /usr/bin/pip ]]; then ln -s pip3 /usr/bin/pip; fi && \
    if [[ ! -e /usr/bin/python ]]; then ln -sf /usr/bin/python3 /usr/bin/python; fi && \
    if [[ -d /root/.cache ]]; then rm -r /root/.cache; fi

COPY rabbitmq_config.sh /opt/init/rabbitmq_config.sh

RUN chmod +x /opt/init/rabbitmq_config.sh

ENTRYPOINT ["/opt/init/rabbitmq_config.sh"]