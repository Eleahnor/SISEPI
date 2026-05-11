FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY graficas.py .

EXPOSE 5003

CMD ["python", "graficas.py"]