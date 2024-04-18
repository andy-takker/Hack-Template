FROM python:3.11-slim
RUN pip install -U --no-cache-dir poetry pip && poetry config virtualenvs.create false

WORKDIR /app

COPY ./pyproject.toml ./poetry.lock* ./app/
RUN poetry install --no-interaction --no-ansi --no-root --without dev

