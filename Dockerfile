FROM python:3.12.1-alpine3.19

WORKDIR /app

ENV SERVER_PORT=8080
ENV POETRY_VERSION=1.8
ENV PYTHONUNBUFFERED=1
ENV POETRY_VIRTUALENVS_CREATE=0

STOPSIGNAL SIGKILL

RUN pip install "poetry==$POETRY_VERSION"

COPY pyproject.toml poetry.lock /app/
RUN poetry install --only=main --no-interaction --no-ansi

COPY . /app/

CMD ["sh", "-c", "exec python3 -m uvicorn avito_sep24:app --host=0.0.0.0 --port=$SERVER_PORT"]