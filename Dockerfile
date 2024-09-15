FROM python:3.10-slim AS builder


ENV PATH="/root/.local/bin:$PATH" \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache


RUN python -m pip install --user pipx \
    && pipx ensurepath \
    && pipx install poetry==1.8.2

WORKDIR /app

COPY pyproject.toml poetry.lock /app/

RUN poetry install --no-root -vvv


FROM python:3.10-slim AS runtime

ENV VIRTUAL_ENV=/app/.venv\
    PATH="/app/.venv/bin:$PATH" 

COPY --from=builder ${VIRTUAL_ENV} ${VIRTUAL_ENV}

WORKDIR /app

COPY . /app

CMD ["sh", "-c", "streamlit run main.py"]