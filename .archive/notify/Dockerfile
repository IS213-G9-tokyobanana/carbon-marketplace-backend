FROM python:3.11-buster
WORKDIR /app

ENV PYTHONFAULTHANDLER=1 \
  PYTHONUNBUFFERED=1 \
  PYTHONHASHSEED=random \
  PIP_NO_CACHE_DIR=off \
  PIP_DISABLE_PIP_VERSION_CHECK=on \
  PIP_DEFAULT_TIMEOUT=100 \
  POETRY_VERSION=1.4.0

RUN pip install "poetry==$POETRY_VERSION"

COPY . ./
RUN poetry config virtualenvs.create false \
  && poetry install --no-interaction --no-ansi

CMD [ "python", "./notify.py" ]