FROM python:3.10-slim
RUN apt-get update && \
    apt-get install -y build-essential cmake libopenblas-dev liblapack-dev \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY requirements.txt .
COPY app/libs/face_recognition_models ./app/libs/face_recognition_models
RUN pip install --upgrade pip && pip install -r requirements.txt
COPY . .
CMD ["gunicorn", "main:app"]