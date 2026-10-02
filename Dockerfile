FROM python:3.12-slim
WORKDIR /app
COPY pyproject.toml README.md LICENSE ./
COPY src ./src
COPY config ./config
RUN pip install --no-cache-dir .
ENV DATAPROOF_DB_PATH=/data/dataproof.db
VOLUME ["/data"]
EXPOSE 8000
CMD ["uvicorn","dataproof.api:app","--host","0.0.0.0","--port","8000"]
