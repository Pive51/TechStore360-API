FROM python:3.10-slim

WORKDIR /code

# Instalar dependencias esenciales del sistema
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./app /code/app

# Comando definitivo para que Render asigne el puerto automáticamente
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "10000"]