FROM python:3.7-alpine3.7
ENV PIP_DISABLE_PIP_VERSION_CHECK=on
RUN pip install poetry
WORKDIR /app
COPY . /app
RUN poetry config settings.virtualenvs.create false && \
        poetry install -v --no-interaction --no-ansi
RUN python -m kings

