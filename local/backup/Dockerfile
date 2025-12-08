FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Creamos la carpeta donde se guardarán los backups dentro del contenedor
RUN mkdir /backups

CMD ["python", "worker.py"]