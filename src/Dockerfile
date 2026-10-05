FROM python:3.13-slim AS base

WORKDIR /src

COPY src/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

FROM base AS development

CMD ["fastapi", "run", "--port", "8080", "main.py"]

FROM base AS production

COPY src/ .

CMD ["fastapi", "run", "--port", "8080", "main.py"]