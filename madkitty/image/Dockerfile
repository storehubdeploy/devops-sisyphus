FROM python:3.8.0-alpine

WORKDIR /app

RUN apk add --no-cache --virtual .build-deps alpine-sdk && \
    pip3 install --no-cache-dir fastapi uvicorn aioredis python-dotenv && \
    apk del .build-deps

COPY main.py .env ./

CMD ["python3","main.py"]
