# Dockerfile completo com debug
FROM python:3.10-slim AS builder

# Instalar dependências de sistema
RUN apt-get update && \
    apt-get install -y build-essential cmake libopenblas-dev liblapack-dev git && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copiar arquivos de dependências e o pacote local
COPY requirements.txt .
COPY app/libs/face_recognition_models ./app/libs/face_recognition_models

# Debug: listar estrutura de /app
RUN echo "=== LIST /app ===" && ls -R /app
# Debug: exibir conteúdo de requirements.txt
RUN echo "=== CAT requirements.txt ===" && cat /app/requirements.txt
# Debug: listar estrutura do pacote local
RUN echo "=== LIST face_recognition_models ===" && ls -R /app/app/libs/face_recognition_models

# Instalar dependências Python
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copiar restante do código
COPY . .

# Comando para iniciar a aplicação
CMD ["gunicorn", "main:app"]

# Passo de debug: instalação com logs verbosos
RUN pip install --upgrade pip && \
    pip install -vvv -r requirements.txt