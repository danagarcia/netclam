FROM python:slim-bullseye

RUN mkdir -p /app/netclam-cp
COPY netclam_cp /app/netclam-cp/
COPY netclam_cp/__init__.py /app/netclam-cp/netclam_cp/
COPY README.md /app/netclam-cp/
COPY pyproject.toml /app/netclam-cp/
WORKDIR /app/netclam-cp
ENV PYTHONPATH=${PYTHONPATH}:${PWD}

RUN pip3 install poetry
RUN poetry config virtualenvs.create false
RUN poetry install --no-dev

EXPOSE 8080

ENTRYPOINT ["python3", "netclam_cp/main.py"]