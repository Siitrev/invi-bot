FROM python:3.11-alpine3.18

COPY requirements.txt /app/

WORKDIR /app

RUN pip install -r requirements.txt

COPY . .

CMD ["python", "main.py"]