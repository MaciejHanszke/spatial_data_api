FROM python:3.10-slim
ENV PYTHONUNBUFFERED 1 

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    libpq-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY ./requirements.txt .
COPY ./code .

RUN pip install -r requirements.txt

EXPOSE 80

CMD ["uvicorn", "--host", "0.0.0.0", "--port", "80", "main:app"]