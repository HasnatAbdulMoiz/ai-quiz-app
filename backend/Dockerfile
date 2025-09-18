FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY simple_main.py .

EXPOSE 8000

CMD ["python", "simple_main.py"]
