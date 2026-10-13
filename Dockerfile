FROM python:3.14-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_ROOT_USER_ACTION=ignore \
    RUFF_NO_CACHE=true

RUN useradd --create-home app

WORKDIR /app
COPY requirements-dev.txt .
RUN pip install -r requirements-dev.txt

COPY . .

# 権限まわりのテストを意味あるものにするため root では動かさない。
USER app

CMD ["sh", "-c", "ruff check . && ruff format --check . && pytest"]
